import pytest


@pytest.fixture
def dummy_json_token_service_class():
    from fractal.contrib.tokens.services import DummyJsonTokenService

    return DummyJsonTokenService
