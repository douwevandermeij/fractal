from fractal.core.specifications.generic.collections import AndSpecification
from fractal.core.specifications.generic.operators import (
    ContainsSpecification,
    EqualsSpecification,
    GreaterThenEqualSpecification,
    GreaterThenSpecification,
    InSpecification,
    LessThenEqualSpecification,
    LessThenSpecification,
)
from fractal.core.specifications.generic.specification import Specification


def test_parse():
    assert Specification.parse(id=1) == EqualsSpecification("id", 1)
    assert Specification.parse(id_x=1) == EqualsSpecification("id_x", 1)
    assert not Specification.parse(id__x=1)
    assert Specification.parse(id__equals=1) == EqualsSpecification("id", 1)
    assert Specification.parse(id__in=[1]) == InSpecification("id", [1])
    assert Specification.parse(id__contains="a") == ContainsSpecification("id", "a")
    assert Specification.parse(id__lt=1) == LessThenSpecification("id", 1)
    assert Specification.parse(id__lte=1) == LessThenEqualSpecification("id", 1)
    assert Specification.parse(id__gt=1) == GreaterThenSpecification("id", 1)
    assert Specification.parse(id__gte=1) == GreaterThenEqualSpecification("id", 1)
    assert Specification.parse(id=1, name="a") == AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert Specification.parse(id__equals=1, name__equals="a") == AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert Specification.parse(id__equals=1, name="a") == AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert Specification.parse(id=1, name__equals="a") == AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert Specification.parse(id__gt=1, name__contains="a") == AndSpecification(
        [GreaterThenSpecification("id", 1), ContainsSpecification("name", "a")]
    )
