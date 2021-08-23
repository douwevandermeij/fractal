from dataclasses import dataclass

import pytest


@pytest.fixture
def an_object():
    @dataclass
    class AnObject:
        id: str
        name: str = "default_name"

    return AnObject("1")


@pytest.fixture
def inmemory_repository(an_object):
    from fractal.core.repositories.inmemory_repository_mixin import (
        InMemoryRepositoryMixin,
    )

    class InMemoryRepository(InMemoryRepositoryMixin[an_object.__class__]):
        pass

    return InMemoryRepository()
