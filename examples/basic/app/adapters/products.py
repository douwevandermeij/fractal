from app.domain.products import Product, ProductRepository

from fractal.core.repositories.inmemory_repository_mixin import InMemoryRepositoryMixin


class InMemoryProductRepository(ProductRepository, InMemoryRepositoryMixin[Product]):
    pass
