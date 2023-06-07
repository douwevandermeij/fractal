from dataclasses import dataclass
from datetime import datetime
from typing import Any

from fractal.core.models import Model


@dataclass
class Message(Model):
    id: str
    occurred_on: datetime
    event: str
    data: Any
    object_id: str
    aggregate_root_id: str
