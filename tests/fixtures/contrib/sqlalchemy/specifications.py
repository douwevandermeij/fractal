import pytest


@pytest.fixture
def builder():
    from fractal.contrib.sqlalchemy.specifications import (
        SqlAlchemyOrmSpecificationBuilder,
    )

    return SqlAlchemyOrmSpecificationBuilder


@pytest.fixture
def equals_specification():
    from fractal.core.specifications.generic.operators import EqualsSpecification

    return EqualsSpecification("id", 1)


@pytest.fixture
def other_equals_specification():
    from fractal.core.specifications.generic.operators import EqualsSpecification

    return EqualsSpecification("name", "test")


@pytest.fixture
def or_specification(equals_specification, other_equals_specification):
    from fractal.core.specifications.generic.collections import OrSpecification

    return OrSpecification([equals_specification, other_equals_specification])


@pytest.fixture
def and_specification(equals_specification, other_equals_specification):
    from fractal.core.specifications.generic.collections import AndSpecification

    return AndSpecification([equals_specification, other_equals_specification])


@pytest.fixture
def greater_than_specification(equals_specification, other_equals_specification):
    from fractal.core.specifications.generic.operators import GreaterThanSpecification

    return GreaterThanSpecification("id", 1)


@pytest.fixture
def dict_specification(equals_specification, other_equals_specification):
    from fractal.core.specifications.generic.specification import Specification

    class DictSpecification(Specification):
        def __init__(self, collection):
            self.collection = collection

        def is_satisfied_by(self, obj) -> bool:
            raise NotImplementedError

        def to_collection(self) -> dict:
            return self.collection

    return DictSpecification({"id": 1, "test": 2})
