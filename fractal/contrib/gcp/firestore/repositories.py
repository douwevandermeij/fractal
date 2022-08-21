from dataclasses import asdict
from datetime import date
from typing import Iterator, Optional

from google.cloud import firestore
from google.cloud.firestore_v1 import Client

from fractal import Settings
from fractal.contrib.gcp import SettingsMixin
from fractal.contrib.gcp.firestore.specifications import FirestoreSpecificationBuilder
from fractal.core.exceptions import ObjectNotFoundException
from fractal.core.repositories import Entity, Repository
from fractal.core.repositories.sort_repository_mixin import SortRepositoryMixin
from fractal.core.specifications.generic.specification import Specification


def get_firestore_client(settings: Settings):
    if not hasattr(settings, "firestore_client"):
        import firebase_admin
        from firebase_admin import firestore

        cred = None
        if service_account_key := getattr(settings, "GCP_SERVICE_ACCOUNT_KEY"):
            from firebase_admin import credentials

            cred = credentials.Certificate(service_account_key)

        firebase_admin.initialize_app(cred)
        settings.firestore_client = firestore.client()
    return settings.firestore_client


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class FirestoreRepositoryMixin(SettingsMixin, Repository[Entity]):
    """
    https://github.com/GoogleCloudPlatform/python-docs-samples/blob/46fa5a588858021ea32350584a4ee178cd7c1f33/firestore/cloud-client/snippets.py#L62-L66
    """

    entity = Entity

    def __init__(self, *args, **kwargs):
        super(FirestoreRepositoryMixin, self).__init__(*args, **kwargs)

        client: Client = get_firestore_client(self.settings)
        if app_name := getattr(self.settings, "APP_NAME"):
            self.collection = client.collection(
                f"{app_name.lower()}-{self.entity.__name__.lower()}"
            )
        else:
            self.collection = client.collection(self.entity.__name__.lower())

    def add(self, entity: Entity) -> Entity:
        doc_ref = self.collection.document(entity.id)
        doc_ref.set(asdict(entity))
        return entity

    def update(self, entity: Entity, *, upsert=False) -> Entity:
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
        if _filter:
            if isinstance(_filter, list):
                for f in _filter:
                    collection = collection.where(*f)
            else:
                collection = collection.where(*_filter)
        for doc in filter(
            lambda i: specification.is_satisfied_by(AttrDict(i.to_dict())),
            collection.stream(),
        ):
            return self.entity.from_dict(doc.to_dict())
        if self.object_not_found_exception:
            raise self.object_not_found_exception
        raise ObjectNotFoundException(f"{self.entity.__name__} not found!")

    def find(self, specification: Specification = None) -> Iterator[Entity]:
        _filter = FirestoreSpecificationBuilder.build(specification)
        collection = self.collection
        if _filter:
            if isinstance(_filter, list):
                for f in _filter:
                    collection = collection.where(*f)
            else:
                collection = collection.where(*_filter)
        for doc in collection.stream():
            yield self.entity.from_dict(doc.to_dict())

    def is_healthy(self) -> bool:
        return True


class FirestoreRepositoryDictMixin(FirestoreRepositoryMixin[Entity]):
    def add(self, entity: Entity) -> Entity:
        doc_ref = self.collection.document(entity.id)
        doc_ref.set(entity.asdict(skip_types=(date,)))
        return entity

    def update(self, entity: Entity, *, upsert=False) -> Entity:
        if not upsert:
            doc_ref = self.collection.document(entity.id)
            doc = doc_ref.get()
            if doc.exists:
                doc_ref.set(entity.asdict(skip_types=(date,)))
            return entity
        return self.add(entity)


class FirestoreSortRepositoryMixin(SortRepositoryMixin[Entity]):
    def find_sort(
        self, specification: Specification = None, *, order_by: str = "", limit: int = 0
    ) -> Iterator[Entity]:
        _filter = FirestoreSpecificationBuilder.build(specification)
        collection = self.collection
        if _filter:
            if isinstance(_filter, list):
                for f in _filter:
                    collection = collection.where(*f)
            else:
                collection = collection.where(*_filter)
        if order_by:
            if reverse := order_by.startswith("-"):
                order_by = order_by[1:]
            collection = collection.order_by(
                order_by,
                direction=firestore.Query.DESCENDING
                if reverse
                else firestore.Query.ASCENDING,
            )
        if limit:
            collection = collection.limit(limit)
        for doc in collection.stream():
            yield self.entity.from_dict(doc.to_dict())
