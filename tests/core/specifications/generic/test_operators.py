from dataclasses import make_dataclass

from fractal.core.specifications.generic.operators import (
    ContainsSpecification,
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    NotSpecification,
)


def test_not_specification():
    spec = NotSpecification(EqualsSpecification("id", 2))
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_in_specification():
    spec = InSpecification("id", [1, 2, 3])
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_equals_specification():
    spec = EqualsSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_less_than_specification():
    spec = LessThanSpecification("id", 2)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_less_than_equal_specification():
    spec = LessThanEqualSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_greater_than_specification():
    spec = GreaterThanSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=2)))


def test_greater_than_equal_specification():
    spec = GreaterThanEqualSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_contains_specification():
    spec = ContainsSpecification("name", "a")
    DC = make_dataclass("DC", [("name", str)])
    assert spec.is_satisfied_by(DC(**dict(name="fractal")))
