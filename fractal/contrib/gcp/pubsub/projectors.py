import logging
from datetime import datetime

from google.cloud import pubsub_v1

from fractal.core.event_sourcing.event import BasicSendingEvent
from fractal.core.event_sourcing.event_projector import EventProjector
from fractal.core.event_sourcing.message import Message

logger = logging.getLogger("api")


class PubSubEventBusProjector(EventProjector):
    """
    https://cloud.google.com/pubsub/docs/quickstart-client-libraries#pubsub-client-libraries-python
    """

    def __init__(self, project_id):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        self.project_path = f"projects/{project_id}"

    def project(self, id: str, event: BasicSendingEvent):
        # The `topic_path` method creates a fully qualified identifier
        # in the form `projects/{project_id}/topics/{topic_id}`
        topic_path = self.publisher.topic_path(self.project_id, event.topic)

        # Check if topic exists
        if topic_path not in [
            t.name
            for t in self.publisher.list_topics(request={"project": self.project_path})
        ]:
            logger.error(f"Topic doesn't exist '{topic_path}'")

        # Wrap event in a message
        message = Message(
            id,
            datetime.utcnow(),
            event.__class__.__name__,
            event.to_json(),
        )

        # Data must be a bytestring
        data = message.to_json().encode("utf-8")

        # When you publish a message, the client returns a future.
        future = self.publisher.publish(topic_path, data=data)
        logger.debug(f"{data} sent to Google PubSub - message nr: {future.result()}")
