from typing import Optional

from fractal import Fractal
from fractal.contrib.roles.models import Methods, Role
from fractal.contrib.roles.services import BaseRolesService
from fractal.core.utils.application_context import ApplicationContext
from fractal.core.utils.settings import Settings


class Admin(Role):
    def __getattr__(self, item):
        return Methods()


class DummyRolesService(BaseRolesService):
    def __init__(self):
        self.roles = [Admin()]


class DummyTokenRolesFractal(Fractal):
    def __init__(self, context: ApplicationContext, settings: Optional[Settings]):
        self.context = context
        self.token_service = getattr(context, "token_service")
        if roles_service := getattr(context, "roles_service", None):
            self.roles_service = roles_service
        else:
            context.install_service(DummyRolesService, name="roles_service")
        self.settings = settings
        super(DummyTokenRolesFractal, self).__init__()
