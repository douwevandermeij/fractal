from abc import abstractmethod
from typing import Any, Collection, List

from fractal.core.specifications.generic.specification import Specification


class CollectionSpecification(Specification):
    def __init__(self, specifications: List[Specification]):
        self.specifications = specifications

    @abstractmethod
    def is_satisfied_by(self, obj: Any) -> bool:
        raise NotImplementedError

    def to_collection(self) -> Collection:
        return self.specifications

    def and_spec(self, specification: Specification):
        if isinstance(specification, CollectionSpecification):
            self.specifications += specification.specifications
        else:
            self.specifications.append(specification)

    def or_spec(self, specification: Specification):
        self.and_spec(specification)


class AndSpecification(CollectionSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return all([spec.is_satisfied_by(obj) for spec in self.specifications])


class OrSpecification(CollectionSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return any([spec.is_satisfied_by(obj) for spec in self.specifications])


class InSpecification(Specification):
    def __init__(self, field: str, values: List[Any]):
        self.field = field
        self.values = values

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) in self.values

    def to_collection(self) -> Collection:
        return {self.field, self.values}
