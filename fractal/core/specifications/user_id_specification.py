from typing import Any, Collection

from fractal.core.specifications.generic.specification import Specification


class UserIdSpecification(Specification):
    def __init__(self, user_id: str):
        self.user_id = user_id

    def is_satisfied_by(self, obj: Any) -> bool:
        return obj.user_id == self.user_id

    def to_collection(self) -> Collection:
        return dict(user_id=self.user_id)
