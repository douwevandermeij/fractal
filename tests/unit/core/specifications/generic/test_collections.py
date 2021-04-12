from dataclasses import make_dataclass

from fractal.core.specifications.generic.collections import (
    AndSpecification,
    OrSpecification,
)
from fractal.core.specifications.generic.operators import EqualsSpecification


def test_and_specification():
    spec = AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_specification_and():
    spec = AndSpecification([EqualsSpecification("id", 1)]).And(
        EqualsSpecification("name", "a")
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_or_specification():
    spec = OrSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="b")))


def test_specification_or():
    spec = OrSpecification([EqualsSpecification("id", 1)]).Or(
        EqualsSpecification("name", "a")
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=2, name="a")))
