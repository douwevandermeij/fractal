import json
import os
from typing import Iterator, Optional

from fractal.core.exceptions import ObjectNotFoundException
from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.operators import NotSpecification
from fractal.core.specifications.generic.specification import Specification
from fractal.core.specifications.id_specification import IdSpecification
from fractal.core.utils.json_encoder import EnhancedEncoder


class FileRepositoryMixin(Repository[Entity]):
    @property
    def _filename(self) -> str:
        return os.path.join(self.root_dir, f"{self.__class__.__name__}.txt")

    @property
    def _entities(self):
        if not os.path.exists(self._filename):
            return None
        with open(self._filename, "r") as fp:
            for line in fp.readlines():
                yield self.entity(**json.loads(line))

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def add(self, entity: Entity) -> Entity:
        with open(self._filename, "a") as fp:
            fp.write(json.dumps(entity.asdict(), cls=EnhancedEncoder) + "\n")
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        try:
            current = self.find_one(IdSpecification(entity.id))
        except ObjectNotFoundException:
            current = None
        if current or upsert:
            self.remove_one(IdSpecification(entity.id))
            return self.add(entity)

    def remove_one(self, specification: Specification):
        entities = list(self.find(NotSpecification(specification)))
        with open(self._filename, "w") as fp:
            fp.writelines(
                [json.dumps(e.asdict(), cls=EnhancedEncoder) + "\n" for e in entities]
            )

    def find_one(self, specification: Specification) -> Optional[Entity]:
        for entity in filter(
            lambda i: specification.is_satisfied_by(i), self._entities
        ):
            return entity
        if self.object_not_found_exception:
            raise self.object_not_found_exception
        raise ObjectNotFoundException(f"{self.entity.__name__} not found!")

    def find(self, specification: Optional[Specification] = None) -> Iterator[Entity]:
        if specification:
            entities = filter(
                lambda i: specification.is_satisfied_by(i), self._entities
            )
        else:
            entities = self._entities
        for entity in entities:
            yield entity

    def is_healthy(self) -> bool:
        return True
