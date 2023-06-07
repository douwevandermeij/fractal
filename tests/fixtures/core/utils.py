import os
from datetime import datetime, timezone

import pytest


@pytest.fixture
def settings_class():
    from fractal.core.utils.settings import Settings

    class FakeSettings(Settings):
        APP_NAME = os.getenv("APP_NAME", "app_name")
        BASE_DIR = os.getcwd()
        ROOT_DIR = os.getcwd()

        def load(self):
            self.WEBSITE_HOST = os.getenv("WEBSITE_HOST", "http://localhost:8000")

    return FakeSettings


@pytest.fixture
def settings(settings_class):
    return settings_class()


@pytest.fixture
def fake_application_context_class(
    inmemory_repository, fake_service_class, another_fake_service_class, settings_class
):
    from fractal.core.utils.application_context import ApplicationContext

    class FakeApplicationContext(ApplicationContext):
        settings = settings_class()

        def load_internal_services(self):
            super(FakeApplicationContext, self).load_internal_services()

            if os.getenv("FAKE_SERVICE", "") == "another":
                self.fake_service = self.install_service(
                    another_fake_service_class, name="fake_service"
                )()
            else:
                self.fake_service = self.install_service(fake_service_class)()

        def load_repositories(self):
            super(FakeApplicationContext, self).load_repositories()

            self.install_repository(inmemory_repository)

    return FakeApplicationContext


@pytest.fixture
def empty_application_context(settings_class):
    from fractal.core.utils.application_context import ApplicationContext

    class EmptyApplicationContext(ApplicationContext):
        settings = settings_class()

    return EmptyApplicationContext()


@pytest.fixture
def now():
    return datetime.now(timezone.utc)
