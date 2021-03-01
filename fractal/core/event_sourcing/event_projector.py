from abc import ABC, abstractmethod
from typing import Type

from fractal.core.event_sourcing.event import Event


class EventProjector(ABC):
    @abstractmethod
    def project(self, id: str, event: Type[Event]):
        pass
