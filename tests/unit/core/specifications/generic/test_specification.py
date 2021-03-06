from dataclasses import make_dataclass

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


def test_specification_and():
    spec = EqualsSpecification("id", 1).And(EqualsSpecification("name", "a"))
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_specification_or():
    spec = EqualsSpecification("id", 1).Or(EqualsSpecification("name", "a"))
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_specification_not_and():
    spec = Specification.Not(
        EqualsSpecification("id", 1).And(EqualsSpecification("name", "a"))
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="b")))


def test_specification_not_or():
    spec = Specification.Not(
        EqualsSpecification("id", 1).Or(EqualsSpecification("name", "a"))
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=2, name="b")))
