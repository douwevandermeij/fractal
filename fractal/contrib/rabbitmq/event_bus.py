import json
import logging
import threading
from typing import List, Type

from fractal.contrib.rabbitmq.utils import setup_rabbitmq_connection
from fractal.core.command_bus.command_bus import CommandBus
from fractal.core.event_sourcing.event import ReceivingEvent
from fractal.core.event_sourcing.event_bus import EventBus
from fractal.core.event_sourcing.message import Message

logger = logging.getLogger("app")


class RabbitMqEventBus(EventBus):
    def __init__(
        self,
        command_bus: CommandBus,
        host,
        port,
        username,
        password,
        service_name: str,
        event_classes: List[Type[ReceivingEvent]],
        use_thread=False,
    ):
        self.connection, self.channel = setup_rabbitmq_connection(
            host, port, username, password
        )
        for event_class in event_classes:
            logger.info(
                f"Declaring/binding RabbitMq queue: {service_name}_{event_class.__name__}"
            )
            queue = self.channel.queue_declare(  # TODO remove, should be in infra
                queue=f"{service_name}_{event_class.__name__}",
                durable=True,
            )
            self.channel.queue_bind(
                exchange=event_class.__name__,
                queue=queue.method.queue,
            )
            listener = RabbitMqEventBusListener(
                command_bus,
                host,
                port,
                username,
                password,
                event_class,
                queue.method.queue,
            )
            if use_thread:  # TODO should run in separate container
                thread = threading.Thread(target=listener.run)
                thread.setDaemon(True)
                thread.start()
            else:
                listener.run()


class RabbitMqEventBusListener:
    def __init__(
        self,
        command_bus: CommandBus,
        host,
        port,
        username,
        password,
        event_class,
        queue,
    ):
        self.command_bus = command_bus
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.event_class = event_class
        self.queue = queue

    def run(self):
        logger.info(f"Listening to RabbitMq queue: {self.queue}")
        connection, channel = setup_rabbitmq_connection(
            self.host, self.port, self.username, self.password
        )

        def callback(_ch, _method, _properties, body):
            try:
                message = Message(**json.loads(body))
                event = self.event_class(**json.loads(message.data))
                logger.debug("Received event: {}".format(event))
                command = event.to_command()
                if command:
                    self.command_bus.handle(command)
                _ch.basic_ack(_method.delivery_tag)
            except Exception as e:
                logger.exception(e)
                _ch.basic_nack(_method.delivery_tag)

        channel.basic_consume(self.queue, callback)

        try:
            channel.start_consuming()
        finally:
            connection.close()
