from typing import Any, Collection

from fractal.core.specifications.generic.specification import Specification


class AccountIdSpecification(Specification):
    def __init__(self, account_id: Any):
        self.account_id = account_id

    def is_satisfied_by(self, obj: Any) -> bool:
        return obj.account_id == self.account_id

    def to_collection(self) -> Collection:
        return dict(account_id=self.account_id)
