from dataclasses import make_dataclass

from fractal.core.specifications.generic.operators import (
    ContainsSpecification,
    EqualsSpecification,
    GreaterThenEqualSpecification,
    GreaterThenSpecification,
    InSpecification,
    LessThenEqualSpecification,
    LessThenSpecification,
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


def test_less_then_specification():
    spec = LessThenSpecification("id", 2)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_less_then_equal_specification():
    spec = LessThenEqualSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_greater_then_specification():
    spec = GreaterThenSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=2)))


def test_greater_then_equal_specification():
    spec = GreaterThenEqualSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_contains_specification():
    spec = ContainsSpecification("name", "a")
    DC = make_dataclass("DC", [("name", str)])
    assert spec.is_satisfied_by(DC(**dict(name="fractal")))
