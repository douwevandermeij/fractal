from typing import Any, Collection, List

from fractal.core.specifications.generic.specification import Specification


class NotSpecification(Specification):
    def __init__(self, specification: Specification):
        self.specification = specification

    def is_satisfied_by(self, obj: Any) -> bool:
        return not self.specification.is_satisfied_by(obj)

    def to_collection(self) -> Collection:
        return [self.specification]

    def __str__(self):
        return f"{self.__class__.__name__}({self.specification})"


class FieldValueSpecification(Specification):
    def __str__(self):
        return f"{self.__class__.__name__}({self.field}={self.value})"  # NOQA


class InSpecification(FieldValueSpecification):
    def __init__(self, field: str, values: List[Any]):
        self.field = field
        self.value = values

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) in self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class EqualsSpecification(FieldValueSpecification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) == self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class LessThenSpecification(FieldValueSpecification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) < self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class LessThenEqualSpecification(FieldValueSpecification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) <= self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class GreaterThenSpecification(FieldValueSpecification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) > self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class GreaterThenEqualSpecification(FieldValueSpecification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) >= self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class RegexStringMatchSpecification(FieldValueSpecification):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return self.value in getattr(obj, self.field)

    def to_collection(self) -> Collection:
        return {self.field, self.value}
