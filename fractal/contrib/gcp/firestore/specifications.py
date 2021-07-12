from typing import Collection, Optional

from fractal.core.exceptions import DomainException
from fractal.core.specifications.generic.collections import AndSpecification
from fractal.core.specifications.generic.operators import (
    EqualsSpecification,
    GreaterThenEqualSpecification,
    GreaterThenSpecification,
    InSpecification,
    LessThenEqualSpecification,
    LessThenSpecification,
)
from fractal.core.specifications.generic.specification import Specification


class SpecificationNotMappedToFirestore(DomainException):
    code = "SPECIFICATION_NOT_MAPPED_TO_FIRESTORE"
    status_code = 500


class FirestoreSpecificationBuilder:
    @staticmethod
    def build(specification: Specification = None) -> Optional[Collection]:
        if specification is None:
            return None
        elif isinstance(specification, AndSpecification):
            return [
                FirestoreSpecificationBuilder.build(spec)
                for spec in specification.to_collection()
            ]
        elif isinstance(specification, InSpecification):
            return specification.field, "in", specification.value
        elif isinstance(specification, EqualsSpecification):
            return specification.field, "==", specification.value
        elif isinstance(specification, LessThenSpecification):
            return specification.field, "<", specification.value
        elif isinstance(specification, LessThenEqualSpecification):
            return specification.field, "<=", specification.value
        elif isinstance(specification, GreaterThenSpecification):
            return specification.field, ">", specification.value
        elif isinstance(specification, GreaterThenEqualSpecification):
            return specification.field, ">=", specification.value
        elif isinstance(specification.to_collection(), dict):
            for key, value in dict(specification.to_collection()).items():
                return key, "==", value
        raise SpecificationNotMappedToFirestore(
            f"Specification '{specification}' not mapped to Firestore query."
        )
