import os

import pytest


@pytest.fixture
def settings_class():
    from fractal.core.utils.settings import Settings

    class FakeSettings(Settings):
        APP_NAME = os.getenv("APP_NAME", "app_name")

        def load(self):
            self.WEBSITE_HOST = os.getenv("WEBSITE_HOST", "http://localhost:8000")

    return FakeSettings


@pytest.fixture
def settings(settings_class):
    return settings_class()


@pytest.fixture
def fake_application_context_class(
    inmemory_repository, fake_service_class, another_fake_service_class
):
    from fractal.core.utils.application_context import ApplicationContext

    class FakeApplicationContext(ApplicationContext):
        def load_internal_services(self):
            if os.getenv("FAKE_SERVICE", "") == "another":
                self.install_service(another_fake_service_class, name="fake_service")
            else:
                self.install_service(fake_service_class)

        def load_repositories(self):
            self.install_repository(inmemory_repository)

        def load_egress_services(self):
            pass

        def load_event_projectors(self):
            return []

        def load_command_bus(self):
            super(FakeApplicationContext, self).load_command_bus()

        def load_ingress_services(self):
            pass

    return FakeApplicationContext


@pytest.fixture
def empty_application_context():
    from fractal.core.utils.application_context import ApplicationContext

    return ApplicationContext()
