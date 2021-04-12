from typing import Any

from fractal.core.specifications.generic.operators import EqualsSpecification


class IdSpecification(EqualsSpecification):
    def __init__(self, id: Any):
        super(IdSpecification, self).__init__("id", id)
