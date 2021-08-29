import pytest

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), ("id", "==", 1)),
    (
        pytest.lazy_fixture("and_specification"),
        [("id", "==", 1), ("name", "==", "test")],
    ),
    (pytest.lazy_fixture("dict_specification"), [("id", "==", 1), ("test", "==", 2)]),
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(firestore_specification_builder, specification, expected):
    assert firestore_specification_builder.build(specification) == expected
