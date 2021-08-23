import pytest


@pytest.fixture
def service():
    from fractal.core.services import Service

    return Service()


@pytest.fixture
def fake_service_class():
    from fractal.core.services import Service

    class FakeService(Service):
        pass

    return FakeService


@pytest.fixture
def another_fake_service_class():
    from fractal.core.services import Service

    class AnotherFakeService(Service):
        pass

    return AnotherFakeService
