from fractal.core.repositories.inmemory_repository_mixin import InMemoryRepositoryMixin

from app.domain.products import Product, ProductRepository


class InMemoryProductRepository(ProductRepository, InMemoryRepositoryMixin[Product]):
    pass
