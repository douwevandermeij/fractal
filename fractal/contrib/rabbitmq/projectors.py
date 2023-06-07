import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from json import JSONEncoder
from typing import List, Type

import pika

from fractal.contrib.rabbitmq.utils import setup_rabbitmq_connection
from fractal.core.event_sourcing.event import BasicSendingEvent
from fractal.core.event_sourcing.event_projector import EventProjector
from fractal.core.event_sourcing.message import Message

logger = logging.getLogger("app")


class RabbitMqEventBusProjector(EventProjector):
    def __init__(
        self,
        host,
        port,
        username,
        password,
        service_name: str,
        event_classes: List[Type[BasicSendingEvent]],
        json_encoder: Type[JSONEncoder] = None,
    ):
        self.connection, self.channel = setup_rabbitmq_connection(
            host, port, username, password
        )
        self.service_name = service_name
        self.json_encoder = json_encoder
        for klass in event_classes:
            logger.info(f"Declaring RabbitMq exchange: {klass.__name__}")
            self.channel.exchange_declare(  # TODO remove, should be in infra
                exchange=klass.__name__,
                exchange_type="fanout",
                durable=True,
            )

    def project(self, id: str, event: BasicSendingEvent):
        message = Message(
            id=id,
            occurred_on=datetime.now(timezone.utc),
            event=event.__class__.__name__,
            data=json.dumps(asdict(event), cls=self.json_encoder),
            object_id=event.object_id,
            aggregate_root_id=event.aggregate_root_id,
        )

        self.channel.basic_publish(
            exchange=message.event,
            routing_key="",
            body=json.dumps(asdict(message), cls=self.json_encoder).encode(),
            properties=pika.BasicProperties(
                content_type="application/json", delivery_mode=1
            ),
        )
        logger.debug(f"Event sent to EventBus: '{message}'")
