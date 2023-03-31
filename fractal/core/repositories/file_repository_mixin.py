import json
import os
import uuid

from fractal_specifications.generic.operators import (
    EqualsSpecification,
    NotSpecification,
)
from fractal_specifications.generic.specification import Specification

from fractal.core.exceptions import ObjectNotFoundException
from fractal.core.repositories import Entity, FileRepository
from fractal.core.repositories.inmemory_repository_mixin import InMemoryRepositoryMixin
from fractal.core.utils.json_encoder import EnhancedEncoder


class RootDirMixin(object):
    def __init__(self, root_dir: str, *args, **kwargs):
        super(RootDirMixin, self).__init__(*args, **kwargs)

        self.root_dir = root_dir


class FileRepositoryMixin(RootDirMixin, InMemoryRepositoryMixin[Entity]):
    @property
    def _filename(self) -> str:
        return os.path.join(self.root_dir, "db", f"{self.__class__.__name__}.txt")

    @property
    def _entities(self):
        if not os.path.exists(self._filename):
            return None
        with open(self._filename, "r") as fp:
            for line in fp.readlines():
                yield self.entity(**json.loads(line))

    def add(self, entity: Entity) -> Entity:
        with open(self._filename, "a") as fp:
            fp.write(json.dumps(entity.asdict(), cls=EnhancedEncoder) + "\n")
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        try:
            current = self.find_one(EqualsSpecification("id", entity.id))
        except ObjectNotFoundException:
            current = None
        if current or upsert:
            self.remove_one(EqualsSpecification("id", entity.id))
            return self.add(entity)

    def remove_one(self, specification: Specification):
        entities = list(self.find(NotSpecification(specification)))
        with open(self._filename, "w") as fp:
            fp.writelines(
                [json.dumps(e.asdict(), cls=EnhancedEncoder) + "\n" for e in entities]
            )


class FileFileRepositoryMixin(RootDirMixin, FileRepository):
    def upload_file(self, data: bytes, content_type: str, reference: str = "") -> str:
        if not reference:
            reference = str(uuid.uuid4())
        with open(os.path.join(self.root_dir, "media", reference), "wb") as fp:
            fp.write(data)
        return reference

    def get_file(self, reference: str) -> bytes:
        with open(os.path.join(self.root_dir, "media", reference), "rb") as fp:
            return fp.read()

    def delete_file(self, reference: str) -> bool:
        try:
            os.remove(os.path.join(self.root_dir, "media", reference))
            return True
        except Exception:
            return False
