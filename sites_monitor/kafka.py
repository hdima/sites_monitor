import logging
import json
from typing import Dict, Any, Optional

import confluent_kafka # type: ignore

from .monitor import SiteStatus


# FIXME: What to do if some messages can't be delivered?
class KafkaReporter:
    """Reporter to report status of the sites to a Kafka topic"""

    default_timeout = 10

    def __init__(self, report_topic: str, config: Dict[str, Any]) -> None:
        logger = logging.getLogger("kafka.producer")
        self.topic = report_topic
        self._producer = confluent_kafka.Producer(config, logger=logger)

    def report(self, status: SiteStatus) -> None:
        """Report site status to the topic"""
        message: Dict[str, Any] = {
            "url": status.url,
            "result": status.result.value,
            "timestamp": status.timestamp.isoformat(),
        }
        if status.info is not None:
            message["info"] = {
                "status_code": status.info.status_code,
                "response_time": status.info.response_time,
            }
        # TODO: We can define the callback to check delivery status here
        self._producer.produce(self.topic, json.dumps(message))

    def flush(self, timeout: Optional[float] = None) -> int:
        """Wait for all published messages to be delivered

        Return number of messages still in the queue"""
        if timeout is None:
            timeout = self.default_timeout
        return self._producer.flush(timeout)
