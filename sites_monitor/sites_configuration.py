from abc import ABC, abstractmethod
import re
from typing import Iterator, Optional, List, BinaryIO
from urllib.error import URLError


class SiteInfo:

    def __init__(self, url: str, expected_text_pattern: Optional[re.Pattern] = None) -> None:
        self.url = url
        self.expected_text_pattern = expected_text_pattern

    def is_healthy(self, status_code: int) -> bool:
        # FIXME: Maybe we want some configuration driven logic here instead?
        return 200 <= status_code <= 299

    def is_pattern_found(self, reader: BinaryIO) -> bool:
        if not self.expected_text_pattern:
            # Treat it as found when we don't expect any text pattern
            return True
        try:
            # TODO: We can read only until match is found
            return self.expected_text_pattern.search(reader.read()) is not None
        except URLError:
            return False

class SitesConfiguration(ABC):

    @abstractmethod
    def iter_sites(self) -> Iterator[SiteInfo]:
        pass

class StaticSitesConfiguration(SitesConfiguration):

    def __init__(self, sites: List[SiteInfo]) -> None:
        self._sites = sites

    def iter_sites(self) -> Iterator[SiteInfo]:
        return iter(self._sites)
