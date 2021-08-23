from dataclasses import asdict
from typing import Generator, Optional

from google.cloud.firestore_v1 import Client

from fractal.contrib.gcp.firestore.specifications import FirestoreSpecificationBuilder
from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.specification import Specification


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class FirestoreRepositoryMixin(Repository[Entity]):
    """
    https://github.com/GoogleCloudPlatform/python-docs-samples/blob/46fa5a588858021ea32350584a4ee178cd7c1f33/firestore/cloud-client/snippets.py#L62-L66
    """

    entity = Entity

    def __init__(self, client: Client):
        self.collection = client.collection(self.entity.__name__.lower())

    def add(self, entity: Entity) -> Entity:
        doc_ref = self.collection.document(entity.id)
        doc_ref.set(asdict(entity))
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        if not upsert:
            doc_ref = self.collection.document(entity.id)
            doc = doc_ref.get()
            if doc.exists:
                doc_ref.set(asdict(entity))
            return entity
        return self.add(entity)

    def remove_one(self, specification: Specification):
        entity = self.find_one(specification)
        self.collection.document(entity.id).delete()

    def find_one(self, specification: Specification) -> Optional[Entity]:
        _filter = FirestoreSpecificationBuilder.build(specification)
        collection = self.collection
        if isinstance(_filter, list):
            for f in _filter:
                collection = collection.where(*f)
        else:
            collection = collection.where(*_filter)
        for doc in filter(
            lambda i: specification.is_satisfied_by(AttrDict(i.to_dict())),
            collection.stream(),
        ):
            return self.entity(**doc.to_dict())

    def find(
        self, specification: Specification = None
    ) -> Generator[Entity, None, None]:
        _filter = FirestoreSpecificationBuilder.build(specification)
        collection = self.collection
        if isinstance(_filter, list):
            for f in _filter:
                collection = collection.where(*f)
        else:
            collection = collection.where(*_filter)
        for doc in collection.stream():
            yield self.entity(**doc.to_dict())

    def is_healthy(self) -> bool:
        return True
