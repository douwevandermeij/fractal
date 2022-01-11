from abc import ABC

from fractal import ApplicationContext


class Service(ABC):
    @classmethod
    def install(cls, context: ApplicationContext):
        yield cls()

    def is_healthy(self) -> bool:
        return True
