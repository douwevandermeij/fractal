from abc import ABC
from dataclasses import dataclass
from typing import Dict

import pytest


@pytest.fixture
def sqlalchemy_test_model():
    @dataclass
    class TestModel:
        id: str
        name: str = "test"

    return TestModel


@pytest.fixture
def sqlalchemy_test_model_dao(sqlalchemy_test_model):
    from sqlalchemy import Column, MetaData, String, Table
    from sqlalchemy.orm import Mapper, mapper

    from fractal.contrib.sqlalchemy.repositories import SqlAlchemyDao

    @dataclass
    class TestModelDao(SqlAlchemyDao):
        id: str
        name: str

        @staticmethod
        def from_domain(obj: sqlalchemy_test_model):
            return TestModelDao(
                id=obj.id,
                name=obj.name,
            )

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
            )

    return TestModelDao


@pytest.fixture
def sqlalchemy_application_mapper(sqlalchemy_test_model_dao):
    from sqlalchemy import MetaData

    from fractal.contrib.sqlalchemy.repositories import DaoMapper

    class ApplicationMapper(DaoMapper):
        def application_mappers(self, meta: MetaData):
            sqlalchemy_test_model_dao.mapper(meta, {})

    return ApplicationMapper


@pytest.fixture
def sqlalchemy_test_repository(
    sqlalchemy_test_model, sqlalchemy_test_model_dao, sqlalchemy_application_mapper
):
    from fractal.contrib.sqlalchemy.repositories import SqlAlchemyRepositoryMixin
    from fractal.core.repositories import Repository

    class TestRepository(Repository[sqlalchemy_test_model], ABC):
        entity = sqlalchemy_test_model

    class SqlAlchemyTestRepository(
        TestRepository,
        SqlAlchemyRepositoryMixin[sqlalchemy_test_model, sqlalchemy_test_model_dao],
    ):
        entity_dao = sqlalchemy_test_model_dao
        application_mapper = sqlalchemy_application_mapper

    return SqlAlchemyTestRepository(connection_str="sqlite://")
