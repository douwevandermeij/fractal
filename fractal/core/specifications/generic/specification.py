from abc import ABC, abstractmethod
from typing import Any, Collection


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
        def __parse(**kwargs):
            for k, v in kwargs.items():
                if "__" not in k:
                    from fractal.core.specifications.generic.operators import (
                        EqualsSpecification,
                    )

                    yield EqualsSpecification(k, v)
                else:
                    field, op = k.split("__")
                    Spec = None
                    if op == "equals":
                        from fractal.core.specifications.generic.operators import (
                            EqualsSpecification as Spec,
                        )
                    elif op == "in":
                        from fractal.core.specifications.generic.operators import (
                            InSpecification as Spec,
                        )
                    elif op == "contains":
                        from fractal.core.specifications.generic.operators import (
                            ContainsSpecification as Spec,
                        )
                    elif op == "lt":
                        from fractal.core.specifications.generic.operators import (
                            LessThenSpecification as Spec,
                        )
                    elif op == "lte":
                        from fractal.core.specifications.generic.operators import (
                            LessThenEqualSpecification as Spec,
                        )
                    elif op == "gt":
                        from fractal.core.specifications.generic.operators import (
                            GreaterThenSpecification as Spec,
                        )
                    elif op == "gte":
                        from fractal.core.specifications.generic.operators import (
                            GreaterThenEqualSpecification as Spec,
                        )
                    if Spec:
                        yield Spec(field, v)

        specs = list(__parse(**kwargs))
        if len(specs) > 1:
            from fractal.core.specifications.generic.collections import AndSpecification

            return AndSpecification(specs)
        elif len(specs) == 1:
            return specs[0]
        return None
