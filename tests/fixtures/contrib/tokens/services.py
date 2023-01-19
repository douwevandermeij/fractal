import pytest


@pytest.fixture
def dummy_json_token_service_class():
    from fractal.contrib.fastapi.routers.tokens import FractalDummyJsonTokenService

    return FractalDummyJsonTokenService
