from abc import ABC, abstractmethod
from typing import Generic, Iterator, Optional, TypeVar

from fractal.core.exceptions import DomainException
from fractal.core.specifications.generic.specification import Specification

Entity = TypeVar("Entity")


class Repository(Generic[Entity], ABC):
    entity: Optional[Entity] = None
    object_not_found_exception: Optional[DomainException] = None

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
    def find(self, specification: Specification = None) -> Iterator[Entity]:
        raise NotImplementedError

    @abstractmethod
    def is_healthy(self) -> bool:
        raise NotImplementedError


class FileRepository(Generic[Entity], ABC):
    @abstractmethod
    def upload_file(self, data: bytes, content_type: str, reference: str = "") -> str:
        ...

    @abstractmethod
    def get_file(self, reference: str) -> str:
        ...

    @abstractmethod
    def delete_file(self, reference: str) -> bool:
        ...
