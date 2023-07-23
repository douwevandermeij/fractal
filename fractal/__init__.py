"""Fractal is a scaffolding toolkit for building SOLID logic for your Python applications."""

__version__ = "4.1.2"

from abc import ABC

from fractal.core.utils.application_context import ApplicationContext
from fractal.core.utils.settings import Settings


class FractalException(Exception):
    pass


class Fractal(ABC):
    settings: Settings = None
    context: ApplicationContext = None

    def __init__(self):
        if not self.settings:
            raise FractalException(
                "Fractal service doesn't provide a 'settings' object."
            )
        if not self.context:
            raise FractalException(
                "Fractal service doesn't provide a 'context' object."
            )
