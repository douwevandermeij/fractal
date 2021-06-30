from abc import ABC, abstractmethod
from typing import Generator, Generic, Optional, TypeVar

from fractal.core.specifications.generic.specification import Specification

Entity = TypeVar("Entity")


class Repository(Generic[Entity], ABC):
    @abstractmethod
    def add(self, entity: Entity) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: Entity, upsert=False) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def remove_one(self, specification: Specification):
        raise NotImplementedError

    @abstractmethod
    def find_one(self, specification: Specification) -> Optional[Entity]:
        raise NotImplementedError

    @abstractmethod
    def find(
        self, specification: Specification = None
    ) -> Generator[Entity, None, None]:
        raise NotImplementedError

    @abstractmethod
    def is_healthy(self) -> bool:
        raise NotImplementedError
