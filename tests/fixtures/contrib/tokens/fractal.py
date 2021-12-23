import pytest


def reset(token_service_fractal, settings):
    token_service_fractal.settings.reload(settings)
    token_service_fractal.context.reload()
    return token_service_fractal


@pytest.fixture(autouse=True)
def token_service_fractal(request, empty_application_context, token_service_class, settings):
    from fractal.contrib.tokens.fractal import DummyTokenServiceFractal

    empty_application_context.install_service(token_service_class, name="token_service")

    service = DummyTokenServiceFractal(empty_application_context, settings)

    marker = request.node.get_closest_marker("settings")
    if marker:
        return reset(service, marker.args[0])
    else:
        return reset(service, {})
