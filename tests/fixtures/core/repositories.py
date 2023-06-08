from dataclasses import dataclass

import pytest
from fractal_repositories.core.entity import Entity


@dataclass
class AnObject(Entity):
    id: str
    name: str = "default_name"


@pytest.fixture
def an_object():
    return AnObject("1")


@pytest.fixture
def another_object():
    return AnObject("2", "another_name")


@pytest.fixture
def yet_another_object():
    return AnObject("3", "yet_another_object")


@pytest.fixture
def inmemory_repository():
    from fractal_repositories.mixins.inmemory_repository_mixin import (
        InMemoryRepositoryMixin,
    )

    class InMemoryRepository(InMemoryRepositoryMixin[AnObject]):
        entity = AnObject

    return InMemoryRepository()


@pytest.fixture
def inmemory_filter_repository():
    from fractal_repositories.mixins.filter_repository_mixin import (
        FilterRepositoryMixin,
    )
    from fractal_repositories.mixins.inmemory_repository_mixin import (
        InMemoryRepositoryMixin,
    )

    class InMemoryFilterRepository(
        InMemoryRepositoryMixin[AnObject], FilterRepositoryMixin[AnObject]
    ):
        entity = AnObject

    return InMemoryFilterRepository()


@pytest.fixture
def external_data_inmemory_repository():
    from fractal_repositories.mixins.external_data_inmemory_repository_mixin import (
        ExternalDataInMemoryRepositoryMixin,
    )

    class ExternalDataInMemoryRepository(ExternalDataInMemoryRepositoryMixin[AnObject]):
        entity = AnObject

    return ExternalDataInMemoryRepository(AnObject)
