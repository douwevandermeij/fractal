import pytest
from django.db.models import Q

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), {"id": 1}),
    (pytest.lazy_fixture("or_specification"), Q(id=1) | Q(name="test")),
    (pytest.lazy_fixture("and_specification"), Q(id=1, name="test")),
    (pytest.lazy_fixture("in_specification"), {"field__in": [1, 2, 3]}),
    (pytest.lazy_fixture("less_than_specification"), {"id__lt": 1}),
    (pytest.lazy_fixture("less_than_equal_specification"), {"id__lte": 1}),
    (pytest.lazy_fixture("greater_than_specification"), {"id__gt": 1}),
    (pytest.lazy_fixture("greater_than_equal_specification"), {"id__gte": 1}),
    (pytest.lazy_fixture("regex_string_match_specification"), {"id__regex": ".*abc.*"}),
    (pytest.lazy_fixture("dict_specification"), {"id": 1, "test": 2}),
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(django_specification_builder, specification, expected):
    assert django_specification_builder.build(specification) == expected
