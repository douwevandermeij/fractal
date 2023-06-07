import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from json import JSONEncoder
from typing import List, Type

from kafka import KafkaProducer

from fractal.core.event_sourcing.event import BasicSendingEvent
from fractal.core.event_sourcing.event_projector import EventProjector
from fractal.core.event_sourcing.message import Message

logger = logging.getLogger("app")


class KafkaEventBusProjector(EventProjector):
    def __init__(
        self,
        host,
        port,
        username,
        password,
        service_name: str,
        aggregate: str,
        event_classes: List[Type[BasicSendingEvent]],
        json_encoder: Type[JSONEncoder] = None,
    ):
        self.bootstrap_servers = f"{host}:{port}"
        self.event_classes = event_classes
        self.service_name = service_name
        self.aggregate = aggregate
        self.json_encoder = json_encoder

    def project(self, id: str, event: BasicSendingEvent):
        if type(event) not in self.event_classes:
            return

        message = Message(
            id=id,
            occurred_on=datetime.now(timezone.utc),
            event=event.__class__.__name__,
            data=json.dumps(asdict(event), cls=self.json_encoder),
            object_id=event.object_id,
            aggregate_root_id=event.aggregate_root_id,
        )

        producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        producer.send(
            f"{self.service_name}.{self.aggregate}",
            json.dumps(asdict(message), cls=self.json_encoder).encode(),
        )

        logger.debug(f"Event sent to EventBus: '{message}'")
