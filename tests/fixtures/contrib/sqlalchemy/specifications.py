import pytest


@pytest.fixture
def sqlalchemy_specification_builder():
    from fractal.contrib.sqlalchemy.specifications import (
        SqlAlchemyOrmSpecificationBuilder,
    )

    return SqlAlchemyOrmSpecificationBuilder
