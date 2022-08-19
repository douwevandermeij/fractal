from typing import Optional

from fractal import Fractal
from fractal.contrib.roles.models import Methods, Role
from fractal.contrib.roles.services import BaseRolesService
from fractal.core.utils.application_context import ApplicationContext
from fractal.core.utils.settings import Settings


class Admin(Role):
    def __getattr__(self, item):
        return Methods()


class RolesService(BaseRolesService):
    def __init__(self):
        self.roles = [Admin()]


class DummyTokenRolesFractal(Fractal):
    def __init__(self, context: ApplicationContext, settings: Optional[Settings]):
        self.context = context
        self.token_service = getattr(context, "token_service")
        self.roles_service = context.install_service(RolesService, name="roles_service")
        self.settings = settings
        super(DummyTokenRolesFractal, self).__init__()
