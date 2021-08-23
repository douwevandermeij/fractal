from abc import ABC, abstractmethod

from fractal.core.event_sourcing.event import BasicSendingEvent


class EventProjector(ABC):
    @abstractmethod
    def project(self, id: str, event: BasicSendingEvent):
        """Project the event, usually onto/into something defined in the constructor."""
