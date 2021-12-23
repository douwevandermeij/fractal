from __future__ import annotations

import dataclasses
import logging
from abc import ABC, abstractmethod
from typing import Dict, Generator, Generic, List, Optional, TypeVar, get_type_hints

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ArgumentError, IntegrityError
from sqlalchemy.orm import Mapper, Session, sessionmaker

from fractal.contrib.sqlalchemy.specifications import SqlAlchemyOrmSpecificationBuilder
from fractal.core.exceptions import DomainException
from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.specification import Specification
from fractal.core.specifications.id_specification import IdSpecification

EntityDao = TypeVar("EntityDao")


class UnknownListItemTypeException(DomainException):
    code = "UNKNOWN_LIST_ITEM_TYPE_EXCEPTION"
    status_code = 500


class IntegrityErrorException(DomainException):
    code = "INTEGRITY_ERROR_EXCEPTION"
    status_code = 500


class SqlAlchemyDao(ABC):
    @staticmethod
    @abstractmethod
    def mapper(meta: MetaData, foreign_keys: Dict[str, Mapper]) -> Mapper:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def table(meta: MetaData) -> Table:
        raise NotImplementedError

    @staticmethod
    def from_domain(obj: Entity) -> SqlAlchemyDao:
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
        return self.__add(entity, self.entity_dao)

    def __add(self, entity: Entity, entity_dao_class: SqlAlchemyDao) -> Entity:
        entity_dao = entity_dao_class.from_domain(entity)
        with self:
            try:
                self.session.add(entity_dao)
                self.commit()
            except IntegrityError as e:
                raise IntegrityErrorException(e)
        return entity

    def update(self, entity: Entity, *, upsert=False) -> Entity:
        return self.__update(entity, self.entity_dao, upsert=upsert)

    def __update(
        self, entity: Entity, entity_dao_class: SqlAlchemyDao, *, upsert=False
    ) -> Entity:
        """Recursive function"""
        with self:
            try:
                existing_entity_dao = self._find_one_raw(
                    IdSpecification(entity.id), entity_dao_class=entity_dao_class
                )
            except ArgumentError:
                raise UnknownListItemTypeException(
                    f"DAO '{entity_dao_class}' has an unknown list collection DAO, please add the type for the list."
                )
            if existing_entity_dao:
                self.__update_existing_record(
                    entity, entity_dao_class, existing_entity_dao
                )
                return entity
            elif upsert:
                return self.__add(entity, entity_dao_class)

    def __update_existing_record(self, entity, entity_dao_class, existing_entity_dao):
        updating_entity_dao = entity_dao_class.from_domain(entity)
        regular_fields = []
        list_fields = []

        for k, v in entity_dao_class.__annotations__.items():
            if hasattr(v, "__origin__") and v.__origin__ is list:
                list_fields.append(k)
            else:
                regular_fields.append(k)

        self.__update_main_entity(
            existing_entity_dao, regular_fields, updating_entity_dao
        )
        self.__update_compound_entities(entity, entity_dao_class, list_fields)
        self.commit()

    def __update_main_entity(
        self, existing_entity_dao, regular_fields, updating_entity_dao
    ):
        for k, v in updating_entity_dao.__dict__.items():
            if hasattr(existing_entity_dao, k) and k in regular_fields:
                setattr(existing_entity_dao, k, v)

    def __update_compound_entities(self, entity, entity_dao_class, list_fields):
        for field in list_fields:
            item_dao_class = get_type_hints(entity_dao_class)[field].__args__[0]

            # check for new items
            for item in getattr(entity, field):
                self.__update(item, item_dao_class, upsert=True)

            # check for items to delete
            foreign_key = getattr(entity_dao_class, field).expression.right
            items = list(
                self.session.query(item_dao_class).filter(foreign_key == entity.id)
            )
            item_ids = [item.id for item in getattr(entity, field)]
            for item_dao in items:
                if item_dao.id not in item_ids:
                    self.session.delete(item_dao)

    def remove_one(self, specification: Specification):
        entity = self._find_one_raw(specification)
        if entity:
            self.session.delete(entity)
            self.commit()

    def find_one(self, specification: Specification) -> Optional[Entity]:
        entity = self._find_one_raw(specification)
        if entity:
            return self._dao_to_domain(entity)

    def find(
        self, specification: Optional[Specification] = None
    ) -> Generator[Entity, None, None]:
        entities = self._find_raw(specification)

        if specification:
            entities = filter(lambda i: specification.is_satisfied_by(i), entities)
        for entity in entities:
            yield self._dao_to_domain(entity)

    def _dao_to_domain(self, entity: Entity):
        return self.__dao_to_domain(entity, self.entity, self.entity_dao)

    def __dao_to_domain(
        self, entity: Entity, domain_model: Entity, entity_dao: SqlAlchemyDao
    ):
        """Recursive function"""
        list_fields = []
        for k, v in entity_dao.__annotations__.items():
            if hasattr(v, "__origin__") and v.__origin__ is list:
                list_fields.append(k)
        d = entity.__dict__
        for field in list_fields:
            if hasattr(entity, field):
                item_domain_model = get_type_hints(domain_model)[field].__args__[0]
                item_entity_dao = get_type_hints(entity_dao)[field].__args__[0]
                d[field] = [
                    self.__dao_to_domain(sub_entity, item_domain_model, item_entity_dao)
                    for sub_entity in getattr(entity, field)
                ]
        fields = set(f.name for f in dataclasses.fields(domain_model))
        return domain_model(**{k: v for k, v in d.items() if k in fields})

    def _find_one_raw(
        self,
        specification: Specification,
        *,
        entity_dao_class: Optional[SqlAlchemyDao] = None,
    ) -> Optional[Entity]:
        entities = self._find_raw(specification, entity_dao_class=entity_dao_class)

        for entity in filter(lambda i: specification.is_satisfied_by(i), entities):
            return entity

    def _find_raw(
        self,
        specification: Optional[Specification],
        *,
        entity_dao_class: Optional[SqlAlchemyDao] = None,
    ) -> List[Entity]:
        _filter = {}
        if specification:
            _filter = SqlAlchemyOrmSpecificationBuilder.build(specification)
        if isinstance(_filter, list):
            entities = []
            for f in _filter:
                entities.extend(
                    list(
                        self.session.query(
                            entity_dao_class or self.entity_dao
                        ).filter_by(**dict(f))
                    )
                )
            return entities
        else:
            return self.session.query(entity_dao_class or self.entity_dao).filter_by(
                **dict(_filter)
            )

    def is_healthy(self) -> bool:
        try:
            with self:
                self.session.execute("SELECT 1")
        except Exception as e:
            logging.exception(f"Database is unhealthy! {e}")
            return False
        return True
