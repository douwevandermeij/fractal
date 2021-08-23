from abc import ABC, abstractmethod

from fractal.core.event_sourcing.event import BasicSendingEvent


class EventProjector(ABC):
    @abstractmethod
    def project(self, id: str, event: BasicSendingEvent):
        pass
