from abc import ABC
from dataclasses import dataclass  # NOQA

from pydantic.dataclasses import dataclass

from fractal.core.models import Model
from fractal.core.repositories import Repository


@dataclass
class Product(Model):
    id: str
    name: str


class ProductRepository(Repository[Product], ABC):
    pass
