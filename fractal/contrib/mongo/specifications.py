import re
from typing import Collection, Optional

from fractal.core.exceptions import DomainException
from fractal.core.specifications.generic.collections import (
    AndSpecification,
    OrSpecification,
)
from fractal.core.specifications.generic.operators import (
    EqualsSpecification,
    GreaterThenEqualSpecification,
    GreaterThenSpecification,
    InSpecification,
    LessThenEqualSpecification,
    LessThenSpecification,
    RegexStringMatchSpecification,
)
from fractal.core.specifications.generic.specification import Specification


class SpecificationNotMappedToMongo(DomainException):
    code = "SPECIFICATION_NOT_MAPPED_TO_MONGO"
    status_code = 500


class MongoSpecificationBuilder:
    @staticmethod
    def build(specification: Specification = None) -> Optional[Collection]:
        if specification is None:
            return None
        elif isinstance(specification, AndSpecification):
            return {
                "$and": [
                    MongoSpecificationBuilder.build(spec)
                    for spec in specification.to_collection()
                ]
            }
        elif isinstance(specification, OrSpecification):
            return {
                "$or": [
                    MongoSpecificationBuilder.build(spec)
                    for spec in specification.to_collection()
                ]
            }
        elif isinstance(specification, InSpecification):
            return {specification.field: {"$in": specification.value}}
        elif isinstance(specification, EqualsSpecification):
            return {specification.field: {"$eq": specification.value}}
        elif isinstance(specification, LessThenSpecification):
            return {specification.field: {"$lt": specification.value}}
        elif isinstance(specification, LessThenEqualSpecification):
            return {specification.field: {"$lte": specification.value}}
        elif isinstance(specification, GreaterThenSpecification):
            return {specification.field: {"$gt": specification.value}}
        elif isinstance(specification, GreaterThenEqualSpecification):
            return {specification.field: {"$gte": specification.value}}
        elif isinstance(specification, RegexStringMatchSpecification):
            return {
                specification.field: {"$regex": f".*{re.escape(specification.value)}.*"}
            }
        elif isinstance(specification.to_collection(), dict):
            for key, value in dict(specification.to_collection()).items():
                return {key: {"$eq": value}}
        raise SpecificationNotMappedToMongo(
            f"Specification '{specification}' not mapped to Mongo query."
        )
