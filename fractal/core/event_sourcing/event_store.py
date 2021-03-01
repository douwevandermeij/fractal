from abc import ABC, abstractmethod

from fractal.core.event_sourcing.event_stream import EventStream


class EventStore(ABC):
    @abstractmethod
    def commit(self, event_stream: EventStream, aggregate: str, version: int):
        raise NotImplementedError

    @abstractmethod
    def get_event_stream(self) -> EventStream:
        raise NotImplementedError

    @abstractmethod
    def is_healthy(self) -> bool:
        raise NotImplementedError
