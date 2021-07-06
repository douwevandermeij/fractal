from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, Generator, Generic, List, Optional, TypeVar

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapper, Session, sessionmaker

from fractal.contrib.sqlalchemy.specifications import SqlAlchemyOrmSpecificationBuilder
from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.specification import Specification
from fractal.core.specifications.id_specification import IdSpecification

EntityDao = TypeVar("EntityDao")


class SqlAlchemyDao(ABC):
    @staticmethod
    @abstractmethod
    def mapper(meta: MetaData, foreign_keys: Dict[str, Mapper]) -> Mapper:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def table(meta: MetaData) -> Table:
        raise NotImplementedError


class DaoMapper(ABC):
    instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)
            cls.instance.done = False
        return cls.instance

    def start_mappers(self, engine: Engine):
        if not self.done:
            meta = MetaData()
            self.application_mappers(meta)
            meta.create_all(engine)
            self.done = True

    @abstractmethod
    def application_mappers(self, meta: MetaData):
        raise NotImplementedError


class AbstractUnitOfWork(ABC):
    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.session_factory = None

    def __enter__(self) -> AbstractUnitOfWork:
        self.session = self.session_factory()  # type: Session
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()


class SqlAlchemyRepositoryMixin(
    Generic[Entity, EntityDao], Repository[Entity], SqlAlchemyUnitOfWork
):
    entity = Entity
    entity_dao = EntityDao
    application_mapper = DaoMapper

    def __init__(self, connection_str: str):
        super().__init__()

        self.connection_str = connection_str
        engine = create_engine(
            self.connection_str,
        )

        self.application_mapper().start_mappers(engine)

        self.session_factory = sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )

    def add(self, entity: Entity) -> Entity:
        entity_dao = self.entity_dao.from_domain(entity)
        with self:
            try:
                self.session.add(entity_dao)
                self.commit()
            except IntegrityError:
                raise
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        self.remove_one(IdSpecification(entity.id))
        return self.add(entity)

    def remove_one(self, specification: Specification):
        if entity := self._find_one_raw(specification):
            self.session.delete(entity)
            self.commit()

    def find_one(self, specification: Specification) -> Optional[Entity]:
        entity = self._find_one_raw(specification)
        if entity:
            return self.entity(**entity.__dict__)

    def find(
        self, specification: Optional[Specification] = None
    ) -> Generator[Entity, None, None]:
        entities = self._find_raw(specification)

        if specification:
            entities = filter(lambda i: specification.is_satisfied_by(i), entities)
        for entity in entities:
            d = entity.__dict__
            if "_sa_instance_state" in d:
                del d["_sa_instance_state"]
            yield self.entity(**d)

    def _find_one_raw(self, specification: Specification) -> Optional[Entity]:
        entities = self._find_raw(specification)

        for entity in filter(lambda i: specification.is_satisfied_by(i), entities):
            return entity

    def _find_raw(self, specification: Optional[Specification]) -> List[Entity]:
        _filter = SqlAlchemyOrmSpecificationBuilder.build(specification)
        if isinstance(_filter, list):
            entities = []
            for f in _filter:
                entities.extend(
                    list(self.session.query(self.entity_dao).filter_by(**dict(f)))
                )
        else:
            entities = self.session.query(self.entity_dao).filter_by(**dict(_filter))
        return entities

    def is_healthy(self) -> bool:
        try:
            with self:
                self.session.execute("SELECT 1")
        except Exception as e:
            logging.exception(f"Database is unhealthy! {e}")
            return False
        return True
