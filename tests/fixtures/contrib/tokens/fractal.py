import pytest


def reset(dummy_token_service_fractal, settings):
    dummy_token_service_fractal.settings.reload(settings)
    dummy_token_service_fractal.context.reload()
    return dummy_token_service_fractal


@pytest.fixture
def dummy_token_service_fractal(token_service_application_context, settings):
    from fractal.contrib.tokens.fractal import DummyTokenServiceFractal

    return DummyTokenServiceFractal(token_service_application_context, settings)
