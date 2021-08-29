import pytest

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), {"id": 1}),
    (pytest.lazy_fixture("or_specification"), [{"id": 1}, {"name": "test"}]),
    (pytest.lazy_fixture("and_specification"), {"id": 1, "name": "test"}),
    (pytest.lazy_fixture("dict_specification"), {"id": 1, "test": 2}),
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(sqlalchemy_specification_builder, specification, expected):
    assert sqlalchemy_specification_builder.build(specification) == expected


def test_build_error(sqlalchemy_specification_builder, greater_than_specification):
    from fractal.contrib.sqlalchemy.specifications import (
        SpecificationNotMappedToSqlAlchemyOrm,
    )

    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        sqlalchemy_specification_builder.build(greater_than_specification)
