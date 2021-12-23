from dataclasses import dataclass

import pytest


@dataclass
class AnObject:
    id: str
    name: str = "default_name"


@pytest.fixture
def an_object():
    return AnObject("1")


@pytest.fixture
def another_object():
    return AnObject("2", "another_name")


@pytest.fixture
def inmemory_repository():
    from fractal.core.repositories.inmemory_repository_mixin import (
        InMemoryRepositoryMixin,
    )

    class InMemoryRepository(InMemoryRepositoryMixin[AnObject]):
        pass

    return InMemoryRepository()


@pytest.fixture
def inmemory_filter_repository():
    from fractal.core.repositories.inmemory_repository_mixin import (
        InMemoryRepositoryMixin,
    )
    from fractal.core.repositories.filter_repository_mixin import FilterRepositoryMixin

    class InMemoryFilterRepository(InMemoryRepositoryMixin[AnObject], FilterRepositoryMixin[AnObject]):
        pass

    return InMemoryFilterRepository()


@pytest.fixture
def external_data_inmemory_repository():
    from fractal.core.repositories.external_data_inmemory_repository_mixin import (
        ExternalDataInMemoryRepositoryMixin,
    )

    class ExternalDataInMemoryRepository(ExternalDataInMemoryRepositoryMixin[AnObject]):
        pass

    return ExternalDataInMemoryRepository(AnObject)
