from typing import List, Optional

from pydantic.main import BaseModel


class AdapterInfo(BaseModel):
    adapter: str
    status_ok: Optional[bool]


class Info(BaseModel):
    adapters: List[AdapterInfo]
