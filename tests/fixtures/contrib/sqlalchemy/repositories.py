from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, List

import pytest
from fractal_repositories.core.entity import Entity


@pytest.fixture
def sqlalchemy_test_model(sqlalchemy_test_sub_model):
    @dataclass
    class TestModel(Entity):
        id: str
        name: str = "test"
        description: str = "test"
        items: List[sqlalchemy_test_sub_model] = field(default_factory=list)

    return TestModel


@pytest.fixture
def sqlalchemy_test_sub_model():
    @dataclass
    class TestSubModel(Entity):
        id: str
        name: str = "test"
        item_id: str = ""

    return TestSubModel


@pytest.fixture
def sqlalchemy_test_model_dao(sqlalchemy_test_model, sqlalchemy_test_sub_model_dao):
    from sqlalchemy import Column, MetaData, String, Table
    from sqlalchemy.orm import Mapper, mapper

    from fractal.contrib.sqlalchemy.repositories import SqlAlchemyDao

    @dataclass
    class TestModelDao(SqlAlchemyDao):
        id: str
        name: str
        description: str
        items: List[sqlalchemy_test_sub_model_dao] = field(default_factory=list)

        @staticmethod
        def from_domain(obj: sqlalchemy_test_model):
            dao = TestModelDao(
                id=obj.id,
                name=obj.name,
                description=obj.description,
            )
            dao.items = [
                sqlalchemy_test_sub_model_dao.from_domain(e) for e in obj.items
            ]
            return dao

        @staticmethod
        def mapper(meta: MetaData, foreign_keys: Dict[str, Mapper]) -> Mapper:
            return mapper(
                TestModelDao,
                TestModelDao.table(meta),
            )

        @staticmethod
        def table(meta: MetaData) -> Table:
            return Table(
                "test_model",
                meta,
                Column("id", String(), primary_key=True),
                Column("name", String()),
                Column("description", String()),
            )

    return TestModelDao


@pytest.fixture
def sqlalchemy_test_model_dao_error(
    sqlalchemy_test_model, sqlalchemy_test_sub_model_dao
):
    from fractal_specifications.contrib.sqlalchemy.repositories import SqlAlchemyDao
    from sqlalchemy import Column, MetaData, String, Table
    from sqlalchemy.orm import Mapper, mapper

    @dataclass
    class TestModelDao(SqlAlchemyDao):
        id: str
        name: str
        description: str
        items: List = field(
            default_factory=list
        )  # no typing for list items will result in error

        @staticmethod
        def from_domain(obj: sqlalchemy_test_model):
            dao = TestModelDao(
                id=obj.id,
                name=obj.name,
                description=obj.description,
            )
            dao.items = [
                sqlalchemy_test_sub_model_dao.from_domain(e) for e in obj.items
            ]
            return dao

        @staticmethod
        def mapper(meta: MetaData, foreign_keys: Dict[str, Mapper]) -> Mapper:
            return mapper(
                TestModelDao,
                TestModelDao.table(meta),
            )

        @staticmethod
        def table(meta: MetaData) -> Table:
            return Table(
                "test_model",
                meta,
                Column("id", String(), primary_key=True),
                Column("name", String()),
                Column("description", String()),
            )

    return TestModelDao


@pytest.fixture
def sqlalchemy_test_sub_model_dao(sqlalchemy_test_sub_model):
    from sqlalchemy import Column, ForeignKey, MetaData, String, Table
    from sqlalchemy.orm import Mapper, mapper, relationship

    from fractal.contrib.sqlalchemy.repositories import SqlAlchemyDao

    @dataclass
    class TestSubModelDao(SqlAlchemyDao):
        id: str
        name: str
        item_id: str

        @staticmethod
        def from_domain(obj: sqlalchemy_test_sub_model):
            return TestSubModelDao(
                id=obj.id,
                name=obj.name,
                item_id=obj.item_id,
            )

        @staticmethod
        def mapper(meta: MetaData, foreign_keys: Dict[str, Mapper]) -> Mapper:
            return mapper(
                TestSubModelDao,
                TestSubModelDao.table(meta),
                properties={
                    k: relationship(v, uselist=False, backref="items")
                    for k, v in foreign_keys.items()
                },
            )

        @staticmethod
        def table(meta: MetaData) -> Table:
            return Table(
                "test_sub_model",
                meta,
                Column("id", String(), primary_key=True),
                Column("name", String()),
                Column("item_id", ForeignKey("test_model.id")),
            )

    return TestSubModelDao


@pytest.fixture
def sqlalchemy_application_mapper(
    sqlalchemy_test_model_dao, sqlalchemy_test_sub_model_dao
):
    from sqlalchemy import MetaData

    from fractal.contrib.sqlalchemy.repositories import DaoMapper

    class ApplicationMapper(DaoMapper):
        def application_mappers(self, meta: MetaData):
            mapper = sqlalchemy_test_model_dao.mapper(meta, {})
            sqlalchemy_test_sub_model_dao.mapper(meta, {"_test_model": mapper})

    return ApplicationMapper


@pytest.fixture
def sqlalchemy_application_mapper_error(
    sqlalchemy_test_model_dao_error, sqlalchemy_test_sub_model_dao
):
    from sqlalchemy import MetaData

    from fractal.contrib.sqlalchemy.repositories import DaoMapper

    class ApplicationMapper(DaoMapper):
        def application_mappers(self, meta: MetaData):
            mapper = sqlalchemy_test_model_dao_error.mapper(meta, {})
            sqlalchemy_test_sub_model_dao.mapper(meta, {"_test_model": mapper})

    return ApplicationMapper


@pytest.fixture
def sqlalchemy_test_repository(
    sqlalchemy_test_model, sqlalchemy_test_model_dao, sqlalchemy_application_mapper
):
    from fractal_repositories.contrib.sqlalchemy.mixins import SqlAlchemyRepositoryMixin
    from fractal_repositories.core.repositories import Repository

    class TestRepository(Repository[sqlalchemy_test_model], ABC):
        entity = sqlalchemy_test_model

    class SqlAlchemyTestRepository(
        TestRepository,
        SqlAlchemyRepositoryMixin[sqlalchemy_test_model, sqlalchemy_test_model_dao],
    ):
        entity_dao = sqlalchemy_test_model_dao
        application_mapper = sqlalchemy_application_mapper

    return SqlAlchemyTestRepository(connection_str="sqlite://")


@pytest.fixture
def sqlalchemy_test_repository_error(
    sqlalchemy_test_model,
    sqlalchemy_test_model_dao_error,
    sqlalchemy_application_mapper_error,
):
    from fractal_repositories.contrib.sqlalchemy.mixins import SqlAlchemyRepositoryMixin
    from fractal_repositories.core.repositories import Repository

    class TestRepository(Repository[sqlalchemy_test_model], ABC):
        entity = sqlalchemy_test_model

    class SqlAlchemyTestRepository(
        TestRepository,
        SqlAlchemyRepositoryMixin[
            sqlalchemy_test_model, sqlalchemy_test_model_dao_error
        ],
    ):
        entity_dao = sqlalchemy_test_model_dao_error
        application_mapper = sqlalchemy_application_mapper_error

    return SqlAlchemyTestRepository(connection_str="sqlite://")
