from abc import ABC, abstractmethod
from typing import Generic, Iterator

from fractal.core.repositories import Entity
from fractal.core.specifications.generic.specification import Specification


class SortRepositoryMixin(Generic[Entity], ABC):
    @abstractmethod
    def find_sort(
        self, specification: Specification = None, *, order_by: str = "", limit: int = 0
    ) -> Iterator[Entity]:
        ...

    def find_one_sort(
        self, specification: Specification = None, *, order_by: str = ""
    ) -> Entity:
        for release in self.find_sort(
            specification=specification, order_by=order_by, limit=1
        ):
            return release


class InMemorySortRepositoryMixin(SortRepositoryMixin[Entity]):
    def find_sort(
        self, specification: Specification = None, *, order_by: str = "", limit: int = 0
    ) -> Iterator[Entity]:
        entities = self.find(specification)
        if order_by:
            if reverse := order_by.startswith("-"):
                order_by = order_by[1:]
            entities = sorted(
                entities, key=lambda i: getattr(i, order_by), reverse=reverse
            )
        for i, entity in enumerate(entities):
            if limit and i == limit:
                break
            yield entity
