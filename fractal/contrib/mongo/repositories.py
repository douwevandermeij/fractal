import logging
from typing import Generator, Optional, Tuple

from pymongo import MongoClient
from pymongo.database import Database

from fractal.contrib.mongo.specifications import MongoSpecificationBuilder
from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.specification import Specification

logger = logging.getLogger("app")


def setup_mongo_connection(
    host, port, username, password, database
) -> Tuple[MongoClient, Database]:
    if host == "mongo-mock":
        import mongomock

        client = mongomock.MongoClient()
    else:
        if username:
            connection_string = f"mongodb+srv://{username}:{password}@{host}/{database}"
        else:
            connection_string = f"mongodb://{host}:{port}/{database}"
        connection_string += "?retryWrites=true&w=majority&connect=false"
        client = MongoClient(connection_string)
    db = client[database]
    return client, db


class MongoRepositoryMixin(Repository[Entity]):
    def __init__(self, host, port, username, password, database, collection):
        self.client, self.db = setup_mongo_connection(
            host, port, username, password, database
        )
        self.collection = getattr(self.db, collection)

    def add(self, entity: Entity) -> Entity:
        self.collection.insert_one(entity.asdict())
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        obj = self.collection.find_one(
            dict(
                id=entity.id,
            )
        )
        if not obj:
            if upsert:
                return self.add(entity)
            return
        obj.update(entity.asdict())
        self.collection.update_one(
            dict(
                id=entity.id,
                account_id=entity.account_id,
            ),
            {"$set": obj},
        )
        return entity

    def remove_one(self, specification: Specification):
        self.collection.delete_one(MongoSpecificationBuilder.build(specification))

    def find_one(self, specification: Specification) -> Optional[Entity]:
        for obj in self.collection.find(MongoSpecificationBuilder.build(specification)):
            return self._obj_to_domain(obj)

    def find(
        self, specification: Specification = None
    ) -> Generator[Entity, None, None]:
        for obj in self.collection.find(MongoSpecificationBuilder.build(specification)):
            yield self._obj_to_domain(obj)

    def is_healthy(self) -> bool:
        ok = self.client.server_info().get("ok", False)
        if not ok:
            return False
        return True

    @staticmethod
    def _obj_to_domain(obj) -> Entity:
        raise NotImplementedError
