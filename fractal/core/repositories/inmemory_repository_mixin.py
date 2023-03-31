import uuid
from typing import Dict, Iterator, Optional

from fractal_specifications.generic.specification import Specification

from fractal.core.exceptions import ObjectNotFoundException
from fractal.core.repositories import Entity, FileRepository, Repository


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

    @property
    def _get_entities(self):
        return self._entities if hasattr(self, "_entities") else self.entities.values()

    def find_one(self, specification: Specification) -> Optional[Entity]:
        for entity in filter(
            lambda i: specification.is_satisfied_by(i), self._get_entities
        ):
            return entity
        if self.object_not_found_exception:
            raise self.object_not_found_exception
        raise ObjectNotFoundException(f"{self.entity.__name__} not found!")

    def find(
        self,
        specification: Optional[Specification] = None,
        *,
        offset: int = 0,
        limit: int = 0,
        order_by: str = "id",
    ) -> Iterator[Entity]:
        if specification:
            entities = filter(
                lambda i: specification.is_satisfied_by(i), self._get_entities
            )
        else:
            entities = self._get_entities

        reverse = False
        if order_by.startswith("-"):
            order_by = order_by[1:]
            reverse = True

        entities = sorted(entities, key=lambda i: getattr(i, order_by), reverse=reverse)

        if limit:
            entities = entities[offset : offset + limit]
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
