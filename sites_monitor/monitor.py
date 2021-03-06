from abc import ABC, abstractmethod
import datetime
from enum import Enum, auto
import time
from typing import Iterator, Optional
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from .sites_configuration import SiteInfo, SitesConfiguration


class CheckResult(Enum):
    Unreachable = auto()
    Reachable = auto()
    Healthy = auto()

class CheckInfo:

    def __init__(self, status_code: int, response_time: float) -> None:
        self.status_code = status_code
        self.response_time = response_time

class SiteStatus:

    def __init__(self, url: str, result: CheckResult, info: Optional[CheckInfo] = None,
                 timestamp: Optional[datetime.datetime] = None) -> None:
        if result == CheckResult.Unreachable and info is not None:
            raise ValueError("Unexpected additional information for unreachable site")
        self.url = url
        self.result = result
        self.info = info
        if not timestamp:
            # FIXME: Maybe we want timezone aware datetime here?
            timestamp = datetime.datetime.utcnow()
        self.timestamp = timestamp

class SitesMonitor(ABC):

    @abstractmethod
    def iter_statuses(self) -> Iterator[SiteStatus]:
        pass

class SequentialSitesMonitor(SitesMonitor):

    default_timeout: int = 30

    def __init__(self, sites: SitesConfiguration) -> None:
        self._sites = sites

    def iter_statuses(self) -> Iterator[SiteStatus]:
        for site in self._sites.iter_sites():
            yield self._get_status(site)

    def _get_status(self, site: SiteInfo) -> SiteStatus:
        start_time = time.monotonic()
        try:
            # FIXME: Current implementation handles redirects automatically.
            # Maybe this is not what we want?
            with urlopen(site.url, timeout=self.default_timeout) as r:
                response_time = time.monotonic() - start_time
                status_code = r.getcode()
                info = CheckInfo(status_code, response_time)

                result = CheckResult.Reachable
                if site.is_healthy(status_code) and site.is_pattern_found(r):
                    result = CheckResult.Healthy
                return SiteStatus(site.url, result, info)
        except HTTPError as e:
            response_time = time.monotonic() - start_time
            info = CheckInfo(e.code, response_time)
            return SiteStatus(site.url, CheckResult.Reachable, info)
        except URLError:
            # FIXME: Probably we also want to pass error description here
            return SiteStatus(site.url, CheckResult.Unreachable)
