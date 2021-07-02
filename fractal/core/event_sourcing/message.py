from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Message:
    id: str
    occurred_on: datetime
    event: str
    data: Any
    object_id: str
