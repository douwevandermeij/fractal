import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "context: overrides for adapters in Context")


def reset(fractal, settings):
    fractal.settings.reload(settings)
    fractal.context.reload()
    return fractal


@pytest.fixture
def reset_fractal(fractal):
    def _reset(settings):
        return reset(fractal, settings)

    return _reset
