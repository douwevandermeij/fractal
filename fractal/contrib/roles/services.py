from typing import Set

from fractal.contrib.roles.models import Role
from fractal.core.exceptions import DomainException
from fractal.core.services import Service


class NoPermissionException(DomainException):
    code = "NO_PERMISSION"
    status_code = 403


class RolesService(Service):
    @staticmethod
    def verify_roles(user_roles: Set[Role], required_roles: Set[Role]):
        if not RolesService.verify_roles_check(user_roles, required_roles):
            raise NoPermissionException(
                f"Got '{user_roles}' while one of '{required_roles}' or higher is required."
            )
        return True

    @staticmethod
    def verify_roles_check(user_roles: Set[Role], required_roles: Set[Role]) -> bool:
        return bool(user_roles & required_roles)
