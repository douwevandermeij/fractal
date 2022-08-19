from typing import Callable, Optional
from uuid import UUID

from pydantic.main import BaseModel


class TokenPayload(BaseModel):
    iss: Optional[str]
    sub: Optional[UUID]
    account: Optional[UUID]
    email: Optional[str]
    typ: Optional[str]


class TokenPayloadRoles(TokenPayload):
    roles: Optional[list]
    specification_func: Callable = lambda **kwargs: None
