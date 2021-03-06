import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import re
from threading import Thread
import unittest

from ..monitor import CheckInfo, CheckResult, SiteStatus, SequentialSitesMonitor
from ..sites_configuration import SiteInfo, StaticSitesConfiguration


class TestCheckInfo(unittest.TestCase):

    def test_attributes(self) -> None:
        info = CheckInfo(200, 0.2)
        self.assertEqual(200, info.status_code)
        self.assertEqual(0.2, info.response_time)

class TestSiteStatus(unittest.TestCase):

    def test_attributes(self) -> None:
        url = "http://host/page"
        status = SiteStatus(url, CheckResult.Unreachable)
        self.assertEqual(url, status.url)
        self.assertEqual(CheckResult.Unreachable, status.result)
        self.assertIsNone(status.info)
        self.assertIsInstance(status.timestamp, datetime.datetime)
        self.assertGreater(2, (datetime.datetime.utcnow() - status.timestamp).total_seconds())

class TestSequentialSitesMonitor(unittest.TestCase):

    def setUp(self) -> None:
        class TestHTTPRequestHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path == "/good":
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"text with pattern")
                elif self.path == "/bad":
                    self.send_response(500)
                    self.end_headers()
        self.httpd = HTTPServer(("127.0.0.1", 0), TestHTTPRequestHandler)
        self.base_url = "http://%s:%s" % self.httpd.server_address
        self.thread = Thread(target=self.httpd.serve_forever)
        self.thread.start()

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.thread.join()
        self.httpd.server_close()

    def test_iter_statuses(self) -> None:
        site1 = SiteInfo(self.base_url + "/good", re.compile(b"pattern"))
        site2 = SiteInfo(self.base_url + "/good", re.compile(b"invalid"))
        site3 = SiteInfo(self.base_url + "/bad")
        sites = StaticSitesConfiguration([site1, site2, site3])

        monitor = SequentialSitesMonitor(sites)
        statuses = list(monitor.iter_statuses())
        self.assertEqual(3, len(statuses))

        self.assertEqual(site1.url, statuses[0].url)
        self.assertEqual(CheckResult.Healthy, statuses[0].result)
        self.assertIsNotNone(statuses[0].info)
        self.assertEqual(200, statuses[0].info.status_code) # type: ignore
        self.assertGreater(2, statuses[0].info.response_time) # type: ignore
        self.assertGreater(2, (datetime.datetime.utcnow() - statuses[0].timestamp).total_seconds())

        self.assertEqual(site2.url, statuses[1].url)
        self.assertEqual(CheckResult.Reachable, statuses[1].result)
        self.assertIsNotNone(statuses[1].info)
        self.assertEqual(200, statuses[1].info.status_code) # type: ignore
        self.assertGreater(2, statuses[1].info.response_time) # type: ignore
        self.assertGreater(2, (datetime.datetime.utcnow() - statuses[1].timestamp).total_seconds())

        self.assertEqual(site3.url, statuses[2].url)
        self.assertEqual(CheckResult.Reachable, statuses[2].result)
        self.assertIsNotNone(statuses[2].info)
        self.assertEqual(500, statuses[2].info.status_code) # type: ignore
        self.assertGreater(2, statuses[2].info.response_time) # type: ignore
        self.assertGreater(2, (datetime.datetime.utcnow() - statuses[2].timestamp).total_seconds())
