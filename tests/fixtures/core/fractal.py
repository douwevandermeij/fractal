import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "context: overrides for adapters in Context")


def reset(fractal, settings):
    fractal.settings.reload(settings)
    fractal.context.reload()
    return fractal


@pytest.fixture(autouse=True)
def fractal(request, empty_application_context, settings):
    from fractal.core.utils.fractal import ApplicationFractal

    fractal = ApplicationFractal(empty_application_context, settings)

    marker = request.node.get_closest_marker("settings")
    if marker:
        return reset(fractal, marker.args[0])
    else:
        return reset(fractal, {})


@pytest.fixture(autouse=True)
def token_roles_service_fractal(request, token_service_application_context, settings):
    from fractal.core.utils.fractal import ApplicationFractal

    fractal = ApplicationFractal(token_service_application_context, settings)

    marker = request.node.get_closest_marker("settings")
    if marker:
        return reset(fractal, marker.args[0])
    else:
        return reset(fractal, {})


@pytest.fixture
def reset_fractal(token_roles_service_fractal):
    def _reset(settings):
        return reset(token_roles_service_fractal, settings)

    return _reset
