import json
import logging
import threading
from typing import List, Type

from kafka import KafkaConsumer

from fractal.core.command_bus.command_bus import CommandBus
from fractal.core.event_sourcing.event import ReceivingEvent
from fractal.core.event_sourcing.event_bus import EventBus
from fractal.core.event_sourcing.message import Message

logger = logging.getLogger("app")


class KafkaEventBus(EventBus):
    def __init__(
        self,
        command_bus: CommandBus,
        host,
        port,
        username,
        password,
        service_name: str,
        aggregate: str,
        event_classes: List[Type[ReceivingEvent]],
        use_thread=False,
    ):
        listener = KafkaEventBusListener(
            command_bus,
            host,
            port,
            username,
            password,
            service_name,
            aggregate,
            event_classes,
        )
        if use_thread:  # TODO should run in separate container
            thread = threading.Thread(target=listener.run)
            thread.setDaemon(True)
            thread.start()
        else:
            listener.run()


class KafkaEventBusListener:
    def __init__(
        self,
        command_bus: CommandBus,
        host,
        port,
        username,
        password,
        service_name: str,
        aggregate: str,
        event_classes,
    ):
        self.command_bus = command_bus
        self.bootstrap_servers = f"{host}:{port}"
        self.event_classes = {i.__name__: i for i in event_classes}
        self.service_name = service_name
        self.aggregate = aggregate

    def run(self):
        topic = f"{self.service_name}.{self.aggregate}"
        logger.info(f"Listening to RabbitMq queue: {topic}")

        consumer = KafkaConsumer(topic, bootstrap_servers=self.bootstrap_servers)
        for message in consumer:
            logger.info(f"Received message: {message}")
            message = Message(**json.loads(message.value))
            event = self.event_classes[message.event](**json.loads(message.data))
            logger.info("Received event: {}".format(event))
            command = event.to_command()
            if command:
                self.command_bus.handle(command)
