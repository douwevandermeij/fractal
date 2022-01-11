import uuid

from fractal.core.event_sourcing.event import SendingEvent
from fractal.core.event_sourcing.event_projector import EventProjector
from fractal.core.event_sourcing.event_store import EventStore
from fractal.core.event_sourcing.event_stream import EventStream


class EventStoreProjector(EventProjector):
    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def project(self, id: str, event: SendingEvent):
        self.event_store.commit(
            EventStream(id=str(uuid.uuid4()), events=[event]), aggregate="", version=1
        )
