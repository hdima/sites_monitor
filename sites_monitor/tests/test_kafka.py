import datetime
from datetime import timezone
import logging
import json
import unittest
from unittest.mock import patch

from ..kafka import KafkaReporter
from ..monitor import SiteStatus, CheckInfo, CheckResult


class TestKafkaReporter(unittest.TestCase):

    def test_init(self) -> None:
        topic = "report_topic"
        config = {"bootstrap.servers": "localhost:9094"}
        logger = logging.getLogger("kafka.producer")
        with patch("confluent_kafka.Producer") as producer:
            reporter = KafkaReporter(topic, config)
        self.assertEqual(topic, reporter.topic)
        producer.assert_called_once_with(config, logger=logger)

    def test_report_healthy(self) -> None:
        topic = "report_topic"
        url = "http://host/path"
        status_code = 200
        response_time = 0.2
        with patch("confluent_kafka.Producer") as producer:
            reporter = KafkaReporter(topic, {})
            status = SiteStatus(url, CheckResult.Healthy, CheckInfo(status_code, response_time))
            reporter.report(status)
        produce = producer().produce
        produce.assert_called_once()

        args = produce.call_args.args
        self.assertEqual(2, len(args))
        self.assertEqual(topic, args[0])

        message = json.loads(args[1])
        self.assertEqual(["info", "result", "timestamp", "url"], sorted(message))
        self.assertEqual(url, message["url"])
        self.assertEqual("healthy", message["result"])
        now = datetime.datetime.now(timezone.utc)
        self.assertGreater(2,
            (now - datetime.datetime.fromisoformat(message["timestamp"])).total_seconds())
        self.assertEqual({"status_code": status_code, "response_time": response_time},
                         message["info"])

    def test_flush(self) -> None:
        with patch("confluent_kafka.Producer") as producer:
            reporter = KafkaReporter("report_topic", {})
            reporter.flush()
        producer().flush.assert_called_once_with(reporter.default_timeout)
