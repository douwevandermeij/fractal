import uuid
from dataclasses import dataclass, field
from typing import Generic, List, TypeVar

from fractal.core.event_sourcing.event import Event

E = TypeVar("E", bound=Event)


@dataclass
class EventStream(Generic[E]):
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    events: List[E] = field(default_factory=list)
