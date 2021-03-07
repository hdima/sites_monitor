import io
import re
from typing import Optional
import unittest
from urllib.error import URLError

from ..sites import SiteInfo, StaticSitesConfiguration


class TestSiteInfo(unittest.TestCase):

    def test_attributes(self) -> None:
        url = "http://host/page"
        info = SiteInfo(url)
        self.assertEqual(url, info.url)
        self.assertIsNone(info.expected_text_pattern)

        info2 = SiteInfo(url, re.compile(b"pattern"))
        self.assertEqual(url, info2.url)
        self.assertIsInstance(info2.expected_text_pattern, re.Pattern)

    def test_is_healthy(self) -> None:
        info = SiteInfo("http://host/page")
        self.assertTrue(info.is_healthy(200))
        self.assertTrue(info.is_healthy(299))
        self.assertFalse(info.is_healthy(199))
        self.assertFalse(info.is_healthy(300))

    def test_is_pattern_found(self) -> None:
        url = "http://host/page"
        info = SiteInfo(url)
        self.assertTrue(info.is_pattern_found(io.BytesIO(b"text with pattern")))

        info2 = SiteInfo(url, re.compile(b"pattern"))
        self.assertTrue(info2.is_pattern_found(io.BytesIO(b"text with pattern")))
        self.assertFalse(info2.is_pattern_found(io.BytesIO(b"other text")))

    def test_read_error_during_pattern_search(self) -> None:
        class TestReader:
            def read(self, size: Optional[int] = -1) -> str:
                raise URLError("test error")

        url = "http://host/page"
        info = SiteInfo(url)
        self.assertTrue(info.is_pattern_found(TestReader())) # type: ignore

        info2 = SiteInfo(url, re.compile(b"pattern"))
        self.assertFalse(info2.is_pattern_found(TestReader())) # type: ignore

class TestStaticSitesConfiguration(unittest.TestCase):

    def test_iter_sites(self) -> None:
        info = SiteInfo("http://host/page")
        sites = StaticSitesConfiguration([info])
        self.assertEqual([info], list(sites.iter_sites()))
