from typing import Collection, Optional

from fractal.core.exceptions import DomainException
from fractal.core.specifications.generic.collections import (
    AndSpecification,
    OrSpecification,
)
from fractal.core.specifications.generic.operators import EqualsSpecification
from fractal.core.specifications.generic.specification import Specification


class SpecificationNotMappedToSqlAlchemyOrm(DomainException):
    code = "SPECIFICATION_NOT_MAPPED_TO_SLQALCHEMY_ORM"
    status_code = 500


class SqlAlchemyOrmSpecificationBuilder:
    @staticmethod
    def build(specification: Specification = None) -> Optional[Collection]:
        if specification is None:
            return None
        elif isinstance(specification, OrSpecification):
            return [
                SqlAlchemyOrmSpecificationBuilder.build(spec)
                for spec in specification.to_collection()
            ]
        elif isinstance(specification, AndSpecification):
            return {
                k: v
                for spec in specification.to_collection()
                if (i := SqlAlchemyOrmSpecificationBuilder.build(spec))
                for k, v in dict(i).items()
                if isinstance(i, dict)
            }
        elif isinstance(specification, EqualsSpecification):
            return {specification.field: specification.value}
        elif isinstance(specification.to_collection(), dict):
            for key, value in dict(specification.to_collection()).items():
                return {key: value}
        raise SpecificationNotMappedToSqlAlchemyOrm(
            f"Specification '{specification}' not mapped to SqlAlchemy Orm query."
        )
