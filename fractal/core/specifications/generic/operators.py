from typing import Any, Collection

from fractal.core.specifications.generic.specification import Specification


class EqualsSpecification(Specification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) == self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class LessThenSpecification(Specification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) < self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class LessThenEqualSpecification(Specification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) <= self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class GreaterThenSpecification(Specification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) > self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class GreaterThenEqualSpecification(Specification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) >= self.value

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class RegexStringMatchSpecification(Specification):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    def is_satisfied_by(self, obj: Any) -> bool:
        return self.value in getattr(obj, self.field)

    def to_collection(self) -> Collection:
        return {self.field, self.value}
