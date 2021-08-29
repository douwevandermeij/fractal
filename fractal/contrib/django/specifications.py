import re
from functools import reduce
from typing import Collection, Optional, Union

from django.db.models import Q

from fractal.core.exceptions import DomainException
from fractal.core.specifications.generic.collections import (
    AndSpecification,
    OrSpecification,
)
from fractal.core.specifications.generic.operators import (
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    RegexStringMatchSpecification,
)
from fractal.core.specifications.generic.specification import Specification


class SpecificationNotMappedToDjangoOrm(DomainException):
    code = "SPECIFICATION_NOT_MAPPED_TO_DJANGO_ORM"
    status_code = 500


class DjangoOrmSpecificationBuilder:
    @staticmethod
    def create_q(filter):
        if type(filter) is list:
            return Q(*filter)
        elif type(filter) is dict:
            return Q(**filter)

    @staticmethod
    def build(specification: Specification = None) -> Optional[Union[Collection, Q]]:
        if specification is None:
            return None
        elif isinstance(specification, AndSpecification):
            return reduce(
                lambda x, y: x & y,
                [
                    DjangoOrmSpecificationBuilder.create_q(
                        DjangoOrmSpecificationBuilder.build(spec)
                    )
                    for spec in specification.to_collection()
                ],
            )
        elif isinstance(specification, OrSpecification):
            return reduce(
                lambda x, y: x | y,
                [
                    DjangoOrmSpecificationBuilder.create_q(
                        DjangoOrmSpecificationBuilder.build(spec)
                    )
                    for spec in specification.to_collection()
                ],
            )
        elif isinstance(specification, InSpecification):
            return {f"{specification.field}__in": specification.value}
        elif isinstance(specification, EqualsSpecification):
            return {specification.field: specification.value}
        elif isinstance(specification, LessThanSpecification):
            return {f"{specification.field}__lt": specification.value}
        elif isinstance(specification, LessThanEqualSpecification):
            return {f"{specification.field}__lte": specification.value}
        elif isinstance(specification, GreaterThanSpecification):
            return {f"{specification.field}__gt": specification.value}
        elif isinstance(specification, GreaterThanEqualSpecification):
            return {f"{specification.field}__gte": specification.value}
        elif isinstance(specification, RegexStringMatchSpecification):
            return {
                f"{specification.field}__regex": rf".*{re.escape(specification.value)}.*"
            }
        elif isinstance(specification.to_collection(), dict):
            return specification.to_collection()
        raise SpecificationNotMappedToDjangoOrm(
            f"Specification '{specification}' not mapped to Django Orm query."
        )
