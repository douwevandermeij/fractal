import uuid
from typing import Dict, Iterator, Optional

from fractal.core.exceptions import ObjectNotFoundException
from fractal.core.repositories import Entity, FileRepository, Repository
from fractal.core.specifications.generic.specification import Specification


class InMemoryRepositoryMixin(Repository[Entity]):
    def __init__(self):
        super(InMemoryRepositoryMixin, self).__init__()

        self.entities: Dict[str, Entity] = {}

    def add(self, entity: Entity) -> Entity:
        self.entities[entity.id] = entity
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        if entity.id in self.entities or upsert:
            return self.add(entity)

    def remove_one(self, specification: Specification):
        if obj := self.find_one(specification):
            del self.entities[obj.id]

    def find_one(self, specification: Specification) -> Optional[Entity]:
        for entity in filter(
            lambda i: specification.is_satisfied_by(i), self.entities.values()
        ):
            return entity
        if self.object_not_found_exception:
            raise self.object_not_found_exception
        raise ObjectNotFoundException(f"{self.entity.__name__} not found!")

    def find(self, specification: Optional[Specification] = None) -> Iterator[Entity]:
        if specification:
            entities = filter(
                lambda i: specification.is_satisfied_by(i), self.entities.values()
            )
        else:
            entities = self.entities.values()
        for entity in entities:
            yield entity

    def is_healthy(self) -> bool:
        return True


class InMemoryFileRepositoryMixin(FileRepository[Entity]):
    def __init__(self):
        super(InMemoryFileRepositoryMixin, self).__init__()

        self.files: Dict[str, bytes] = {}

    def upload_file(self, data: bytes, content_type: str, reference: str = "") -> str:
        if not reference:
            reference = str(uuid.uuid4())
        self.files[reference] = data
        return reference

    def get_file(self, reference: str) -> bytes:
        return self.files.get(reference, "")

    def delete_file(self, reference: str) -> bool:
        if reference in self.files:
            del self.files[reference]
            return True
        return False
