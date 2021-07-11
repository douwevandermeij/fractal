"""Fractal is a scaffolding toolkit for building SOLID logic for your Python applications."""

__version__ = "0.2.2"

from abc import ABC


class FractalException(Exception):
    pass


class Fractal(ABC):
    def __init__(self):
        if not hasattr(self, "settings"):
            raise FractalException(
                "Fractal service doesn't have a 'settings' attribute."
            )
        if not hasattr(self, "context"):
            raise FractalException(
                "Fractal service doesn't have a 'context' attribute."
            )
