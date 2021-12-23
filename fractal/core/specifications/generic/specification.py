from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Collection, Iterator


def parse_item(field_op: str, value: Any) -> Specification:
    if "__" not in field_op:
        from fractal.core.specifications.generic.operators import EqualsSpecification

        return EqualsSpecification(field_op, value)
    else:
        field, op = field_op.split("__")
        specification = None
        if op == "equals":
            from fractal.core.specifications.generic.operators import (
                EqualsSpecification as specification,
            )
        elif op == "in":
            from fractal.core.specifications.generic.operators import (
                InSpecification as specification,
            )
        elif op == "contains":
            from fractal.core.specifications.generic.operators import (
                ContainsSpecification as specification,
            )
        elif op == "lt":
            from fractal.core.specifications.generic.operators import (
                LessThanSpecification as specification,
            )
        elif op == "lte":
            from fractal.core.specifications.generic.operators import (
                LessThanEqualSpecification as specification,
            )
        elif op == "gt":
            from fractal.core.specifications.generic.operators import (
                GreaterThanSpecification as specification,
            )
        elif op == "gte":
            from fractal.core.specifications.generic.operators import (
                GreaterThanEqualSpecification as specification,
            )
        if specification:
            return specification(field, value)


def parse(**kwargs) -> Iterator[Specification]:
    for field_op, value in kwargs.items():
        yield parse_item(field_op, value)


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, obj: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def to_collection(self) -> Collection:
        raise NotImplementedError

    def And(self, specification: "Specification") -> "Specification":
        from fractal.core.specifications.generic.collections import AndSpecification

        return AndSpecification([self, specification])

    def Or(self, specification: "Specification") -> "Specification":
        from fractal.core.specifications.generic.collections import OrSpecification

        return OrSpecification([self, specification])

    def __str__(self):
        return self.__class__.__name__

    @staticmethod
    def Not(specification: "Specification") -> "Specification":
        from fractal.core.specifications.generic.operators import NotSpecification

        return NotSpecification(specification)

    @staticmethod
    def parse(**kwargs):
        specs = list(parse(**kwargs))
        if len(specs) > 1:
            from fractal.core.specifications.generic.collections import AndSpecification

            return AndSpecification(specs)
        elif len(specs) == 1:
            return specs[0]
        return None
