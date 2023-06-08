from dataclasses import dataclass
from datetime import datetime
from typing import Any

from fractal_repositories.core.entity import Entity


@dataclass
class Message(Entity):
    id: str
    occurred_on: datetime
    event: str
    data: Any
    object_id: str
    aggregate_root_id: str
