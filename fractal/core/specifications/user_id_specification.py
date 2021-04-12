from typing import Any

from fractal.core.specifications.generic.operators import EqualsSpecification


class UserIdSpecification(EqualsSpecification):
    def __init__(self, user_id: Any):
        super(UserIdSpecification, self).__init__("user_id", user_id)
