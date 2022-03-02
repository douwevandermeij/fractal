import json
import logging
from dataclasses import asdict
from datetime import datetime
from json import JSONEncoder
from typing import Optional, Type

from google.cloud import pubsub_v1

from fractal.core.event_sourcing.event import BasicSendingEvent
from fractal.core.event_sourcing.event_projector import EventProjector
from fractal.core.event_sourcing.message import Message

logger = logging.getLogger("api")


class PubSubEventBusProjector(EventProjector):
    """
    https://cloud.google.com/pubsub/docs/quickstart-client-libraries#pubsub-client-libraries-python
    """

    def __init__(
        self,
        project_id: str,
        topic: str,
        json_encoder: Optional[Type[JSONEncoder]] = None,
    ):
        self.project_id = project_id
        self.topic = topic
        self.publisher = pubsub_v1.PublisherClient()
        self.project_path = f"projects/{project_id}"
        self.json_encoder = json_encoder

    def project(self, id: str, event: BasicSendingEvent):
        # The `topic_path` method creates a fully qualified identifier
        # in the form `projects/{project_id}/topics/{topic_id}`
        topic_path = self.publisher.topic_path(self.project_id, self.topic)

        # Check if topic exists
        if topic_path not in [
            t.name
            for t in self.publisher.list_topics(request={"project": self.project_path})
        ]:
            logger.error(f"Topic doesn't exist '{topic_path}'")

        # Wrap event in a message
        message = Message(
            id=id,
            occurred_on=datetime.utcnow(),
            event=event.__class__.__name__,
            data=json.dumps(asdict(event), cls=self.json_encoder),
            object_id=event.object_id,
            aggregate_root_id=event.aggregate_root_id,
        )

        # Data must be a bytestring
        data = json.dumps(asdict(message), cls=self.json_encoder).encode("utf-8")

        # When you publish a message, the client returns a future.
        future = self.publisher.publish(topic_path, data=data)
        logger.debug(f"{data} sent to Google PubSub - message nr: {future.result()}")
