import pytest


@pytest.fixture
def token_service_class():
    from fractal.contrib.tokens.services import DummyTokenService

    return DummyTokenService
