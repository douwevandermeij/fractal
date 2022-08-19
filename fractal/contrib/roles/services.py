from typing import List

from fractal.contrib.roles.models import Role
from fractal.contrib.tokens.exceptions import NotAllowedException
from fractal.contrib.tokens.models import TokenPayloadRoles
from fractal.core.services import Service


class BaseRolesService(Service):
    roles: List[Role] = []

    def verify(
        self, payload: TokenPayloadRoles, endpoint: str, method: str
    ) -> TokenPayloadRoles:
        for role in self.roles:
            if role.__class__.__name__.lower() in payload.roles:
                if e := getattr(role, endpoint, None):
                    if getattr(e, method, None):
                        if m := getattr(e, method, None):
                            payload.specification_func = m.specification_func
                        return payload
        raise NotAllowedException("No permission!")
