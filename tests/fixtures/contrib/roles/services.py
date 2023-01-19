import pytest


@pytest.fixture
def dummy_roles_service_class():
    from fractal_roles.models import Methods, Role
    from fractal_roles.services import RolesService as BaseRolesService

    from fractal import ApplicationContext
    from fractal.core.services import Service

    class Admin(Role):
        def __getattr__(self, item):
            return Methods()

    class DummyRolesService(BaseRolesService, Service):
        def __init__(self):
            self.roles = [Admin()]

        @classmethod
        def install(cls, context: ApplicationContext):
            yield cls()

    return DummyRolesService
