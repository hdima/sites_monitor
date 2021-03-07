import argparse
import logging
import os
import re
import sys
import time
from typing import Optional, List, Dict, Any, Tuple

import yaml

from .sites import SitesConfiguration, StaticSitesConfiguration, SiteInfo
from .monitor import SequentialSitesMonitor
from .kafka import KafkaReporter


# TODO: Better error reporting
class SitesMonitorConfig:
    """Configuration file reader for sites monitor application"""

    def __init__(self, filename: str) -> None:
        with open(filename, "rb") as f:
            config: Dict[str, Any] = yaml.load(f, Loader=yaml.SafeLoader)
        self.check_interval = self.parse_check_interval(config)
        self.sites = self.parse_sites(config)
        self.report_topic, self.kafka_config = self.parse_kafka_config(config)

    def parse_check_interval(self, config: Dict[str, Any]) -> int:
        """Parse check interval value in seconds"""
        try:
            interval_str: str = config["check_interval"]
        except KeyError:
            raise RuntimeError("No 'check_interval' configuraton value found")
        try:
            interval = int(interval_str)
        except ValueError:
            raise RuntimeError(f"Invalid value for 'check_interval': {interval_str!r}")
        # TODO: We can support suffixes for minutes, hours, etc.
        return interval

    def parse_kafka_config(self, config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Parse kafka topic and general Kafka configuration"""
        try:
            kafka_info: Dict[str, Any] = config["kafka"]
        except KeyError:
            raise RuntimeError("No 'kafka' configuration value found")
        try:
            report_topic: str = kafka_info["report_topic"]
        except KeyError:
            raise RuntimeError("No 'kafka' -> 'report_topic' configuration value found")
        try:
            kafka_config: Dict[str, Any] = kafka_info["config"]
        except KeyError:
            raise RuntimeError("No 'kafka' -> 'config' configuration value found")
        return report_topic, kafka_config

    def parse_sites(self, config: Dict[str, Any]) -> SitesConfiguration:
        """Parse configuration for sites to check"""
        try:
            sites: Dict[str, Any] = config["sites"]
        except KeyError:
            raise RuntimeError("No 'sites' configuration value found")
        sites_info = []
        # TODO: Validate 'url' value
        info: Optional[Dict[str, Any]]
        for url, info in sites.items():
            text_pattern: Optional[re.Pattern] = None
            if info is not None:
                pattern: Optional[str] = info.get("text_pattern")
                if pattern is not None:
                    # FIXME: What encoding we should use here?
                    text_pattern = re.compile(pattern.encode())
            sites_info.append(SiteInfo(url, text_pattern))
        return StaticSitesConfiguration(sites_info)

class SitesMonitor:
    """Monitor to check status of configured sites periodically and report it to a Kafka topic"""

    def get_arg_parser(self) -> argparse.ArgumentParser:
        """Result parser of command line arguments"""
        parser = argparse.ArgumentParser(prog="sites_monitor", description="Sites monitor")
        # TODO: We can add some default location for the configuration file here
        parser.add_argument("--config", required=True, help="path to configuration file")
        return parser

    def main(self, args: Optional[List[str]] = None) -> None:
        """Main entry point for the application"""
        logging.basicConfig(format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
                            level=logging.INFO, stream=sys.stderr)
        logging.info("Starting sites monitor")
        parser = self.get_arg_parser()
        parsed = parser.parse_args(args)
        config = SitesMonitorConfig(parsed.config)
        try:
            self.run(config)
        except KeyboardInterrupt:
            pass
        except:
            logging.critical("Top level exception", exc_info=True)
            os._exit(1)
        logging.info("Stopped sites monitor")

    def run(self, config: SitesMonitorConfig) -> None:
        """Check sites loop"""
        reporter = KafkaReporter(config.report_topic, config.kafka_config)
        monitor = SequentialSitesMonitor(config.sites)
        while True:
            logging.info("Check sites")
            for n, status in enumerate(monitor.iter_statuses()):
                reporter.report(status)
            queued = reporter.flush()
            logging.info("Sent status reports for %d sites. %d messages still in the queue",
                         n + 1, queued)
            logging.info("Wait %d sec before the next check", config.check_interval)
            time.sleep(config.check_interval)
