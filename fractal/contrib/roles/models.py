from dataclasses import dataclass
from typing import Callable, Optional

from fractal_specifications.generic.operators import EqualsSpecification
from fractal_specifications.generic.specification import Specification


class Role:
    def __getattr__(self, item):
        return Methods()

    @staticmethod
    def filter_account(**kwargs) -> Specification:
        return EqualsSpecification("account_id", str(kwargs.get("account")))


@dataclass
class Method:
    specification_func: Callable = lambda **kwargs: None


class Methods:
    get: Optional[Method]
    post: Optional[Method]
    put: Optional[Method]
    delete: Optional[Method]

    def __init__(self, method: Method = None, **kwargs):
        if not method:
            method = Method(lambda **kwargs: Role.filter_account(**kwargs))
        self.get = kwargs["get"] if "get" in kwargs else method
        self.post = kwargs["post"] if "post" in kwargs else method
        self.put = kwargs["put"] if "put" in kwargs else method
        self.delete = kwargs["delete"] if "delete" in kwargs else method
