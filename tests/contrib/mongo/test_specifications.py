import pytest

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), {"id": {"$eq": 1}}),
    (
        pytest.lazy_fixture("or_specification"),
        {"$or": [{"id": {"$eq": 1}}, {"name": {"$eq": "test"}}]},
    ),
    (
        pytest.lazy_fixture("and_specification"),
        {"$and": [{"id": {"$eq": 1}}, {"name": {"$eq": "test"}}]},
    ),
    (
        pytest.lazy_fixture("dict_specification"),
        {"$and": [{"id": {"$eq": 1}}, {"test": {"$eq": 2}}]},
    ),
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(mongo_specification_builder, specification, expected):
    assert mongo_specification_builder.build(specification) == expected
