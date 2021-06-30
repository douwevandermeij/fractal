from typing import Dict, Generator, Optional

from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.specification import Specification


class InMemoryRepositoryMixin(Repository[Entity]):
    def __init__(self):
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

    def find(
        self, specification: Optional[Specification] = None
    ) -> Generator[Entity, None, None]:
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
