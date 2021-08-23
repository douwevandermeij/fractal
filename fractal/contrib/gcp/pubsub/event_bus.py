import json
import logging
import threading
from typing import List, Type

from google.cloud import pubsub_v1

from fractal.core.command_bus.command_bus import CommandBus
from fractal.core.event_sourcing.event import ReceivingEvent
from fractal.core.event_sourcing.event_bus import EventBus
from fractal.core.event_sourcing.message import Message

logger = logging.getLogger("api")


class PubSubEventBus(EventBus):
    """
    https://cloud.google.com/pubsub/docs/quickstart-client-libraries#pubsub-client-libraries-python
    """

    def __init__(
        self,
        command_bus: CommandBus,
        subscription_id: str,
        event_classes: List[Type[ReceivingEvent]],
        project_id: str = None,
        use_thread: bool = False,
    ):
        self.project_id = project_id
        subscriber = pubsub_v1.SubscriberClient()
        with subscriber:
            for event_class in event_classes:
                subscription_path = subscriber.subscription_path(
                    self.project_id, f"{subscription_id}_{event_class.__name__}"
                )
                project_path = f"projects/{project_id}"
                if subscription_path in [
                    t.name
                    for t in subscriber.list_subscriptions(
                        request={"project": project_path}
                    )
                ]:
                    listener = PubSubEventBusListener(
                        command_bus, event_class, subscription_path
                    )
                    if use_thread:  # TODO should run in separate container
                        thread = threading.Thread(target=listener.run)
                        thread.setDaemon(True)
                        thread.start()
                    else:
                        listener.run()
                else:
                    logger.error(f"Cannot subscribe to '{subscription_path}'")


class PubSubEventBusListener:
    def __init__(
        self,
        command_bus: CommandBus,
        event_class,
        subscription_path,
    ):
        self.command_bus = command_bus
        self.event_class = event_class
        self.subscription_path = subscription_path

    def run(self):
        subscriber = pubsub_v1.SubscriberClient()

        def callback(raw_message):
            logger.debug("Received message: {}".format(raw_message))
            try:
                message_data = raw_message.data.decode()
                message = Message(**json.loads(message_data))
                event = self.event_class(**json.loads(message.data))
                logger.debug("Received event: {}".format(event))
                command = event.to_command()
                if command:
                    self.command_bus.handle(command)
                raw_message.ack()
            except Exception as e:
                logger.exception(e)
                raw_message.nack()

        subscriber.subscribe(self.subscription_path, callback=callback)
        logger.debug("Listening for messages on {}..\n".format(self.subscription_path))
