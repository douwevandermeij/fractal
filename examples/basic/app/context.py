from app.settings import Settings

from fractal.core.utils.application_context import ApplicationContext as BaseContext


class ApplicationContext(BaseContext):
    def load_repositories(self):
        from app.domain.products import ProductRepository

        if Settings().PRODUCT_REPOSITORY_BACKEND == "sql":
            """example: some sql adapter code"""
        elif Settings().PRODUCT_REPOSITORY_BACKEND == "file":
            """example: some file adapter code"""
        else:
            from app.adapters.products import InMemoryProductRepository

            self.product_repository: ProductRepository = self.install_repository(
                InMemoryProductRepository(),
            )
