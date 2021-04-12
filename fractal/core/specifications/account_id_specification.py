from typing import Any

from fractal.core.specifications.generic.operators import EqualsSpecification


class AccountIdSpecification(EqualsSpecification):
    def __init__(self, account_id: Any):
        super(AccountIdSpecification, self).__init__("account_id", account_id)
