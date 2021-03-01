from typing import Any, Collection

from fractal.core.specifications.generic.specification import Specification


class IdSpecification(Specification):
    def __init__(self, id: str):
        self.id = id

    def is_satisfied_by(self, obj: Any) -> bool:
        return obj.id == self.id

    def to_collection(self) -> Collection:
        return dict(id=self.id)
