from copy import deepcopy
from typing import List

from fractal.core.event_sourcing.event import Event


class EventSourcedAggregateRoot:
    __events: List[Event] = []

    def record(self, event: Event):
        self.__events.append(event)
        return self

    def release(self):
        released_events = deepcopy(self.__events)
        self.__events.clear()
        return released_events
