from typing import Any, Collection

from fractal.core.specifications.account_id_specification import AccountIdSpecification
from fractal.core.specifications.generic.collections import AndSpecification
from fractal.core.specifications.generic.specification import Specification
from fractal.core.specifications.id_specification import IdSpecification


class ObjectOfAccountSpecification(Specification):
    def __init__(self, object_id: Any, account_id: Any):
        self.specification = AndSpecification(
            [
                AccountIdSpecification(account_id),
                IdSpecification(object_id),
            ]
        )

    def is_satisfied_by(self, obj: Any) -> bool:
        return self.specification.is_satisfied_by(obj)

    def to_collection(self) -> Collection:
        return self.specification.to_collection()
