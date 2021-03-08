from abc import ABC


class Service(ABC):
    @classmethod
    def install(cls, context):
        from fractal.core.utils.application_context import ApplicationContext

        assert issubclass(type(context), ApplicationContext)
        yield cls()

    def is_healthy(self) -> bool:
        return True
