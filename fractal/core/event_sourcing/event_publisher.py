from typing import List

from fractal.core.event_sourcing.event import BasicSendingEvent
from fractal.core.event_sourcing.event_projector import EventProjector
from fractal.core.event_sourcing.event_stream import EventStream


class EventPublisher:
    def __init__(self, projectors: List[EventProjector]):
        self.projectors = projectors

    def publish_event(self, event: BasicSendingEvent):
        self._publish(
            EventStream(
                events=[
                    event,
                ]
            )
        )

    def publish_events(self, events: List[BasicSendingEvent]):
        self._publish(
            EventStream(
                events=events,
            )
        )

    def _publish(self, event_stream: EventStream):
        for event in event_stream.events:
            for projector in self.projectors:
                projector.project(event_stream.id, event)
