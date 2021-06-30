from abc import abstractmethod
from functools import wraps
from typing import Set

from fractal.contrib.roles.models import Role
from fractal.contrib.tokens.services import TokenService
from fractal.core.exceptions import DomainException
from fractal.core.services import Service
from fractal.core.utils.application_context import ApplicationContext


class NoPermissionException(DomainException):
    code = "NO_PERMISSION"
    status_code = 403


class RolesService(Service):
    @abstractmethod
    def verify(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def verify_roles(user_roles: Set[Role], required_roles: Set[Role]):
        if not RolesService.verify_roles_check(user_roles, required_roles):
            raise NoPermissionException(
                f"Got '{user_roles}' while one of '{[role.value for role in required_roles]}' or higher is required."
            )
        return True

    @staticmethod
    def verify_roles_check(user_roles: Set[Role], required_roles: Set[Role]) -> bool:
        return bool(user_roles & required_roles)


class TokenRolesService(RolesService):
    def __init__(self, token_service: TokenService):
        self.token_service = token_service

    def verify(self, required_roles: Set[Role], *args, **kwargs):
        def decorator(func):
            @wraps(func)
            def wrap(token: str, *args, **kwargs):
                payload = self.token_service.verify(token)
                self.verify_roles(set(payload["roles"]), required_roles)
                return func(token, *args, **kwargs)

            return wrap

        return decorator

    @classmethod
    def install(cls, context: ApplicationContext):
        yield cls(*context.get_parameters(["token_service"]))
