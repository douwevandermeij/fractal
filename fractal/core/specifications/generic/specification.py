from abc import ABC, abstractmethod
from typing import Any, Collection


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, obj: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def to_collection(self) -> Collection:
        raise NotImplementedError

    def And(self, specification: "Specification"):
        from fractal.core.specifications.generic.collections import AndSpecification

        return AndSpecification([self, specification])

    def Or(self, specification: "Specification"):
        from fractal.core.specifications.generic.collections import OrSpecification

        return OrSpecification([self, specification])

    def __str__(self):
        return self.__class__.__name__
