import logging
import os
from io import StringIO

from dotenv import load_dotenv

from fractal.core.repositories import Repository
from fractal.core.services import Service
from fractal.core.utils.loggers import init_logging
from fractal.core.utils.string import camel_to_snake


class ApplicationContext(object):
    instance = None

    def __new__(cls, dotenv=True, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls, *args, **kwargs)
            if dotenv:
                load_dotenv()
            cls.instance.load()
        return cls.instance

    def load(self):
        init_logging(os.getenv("LOG_LEVEL", "INFO"))
        self.logger = logging.getLogger("app")
        self.repositories = []

        self.load_internal_services()
        self.load_repositories()
        self.load_ingress_services()
        self.load_egress_services()
        self.load_command_bus()

    def reload(self, defaults: dict):
        self.logger.debug(f"Reloading ApplicationContext with '{defaults}'")
        filelike = StringIO("\n".join([f"{k}={v}" for k, v, in defaults.items()]))
        filelike.seek(0)
        load_dotenv(stream=filelike, override=True)
        self.load()
        ApplicationContext.instance = self

    def adapters(self):
        for name, adapter in self.__dict__.items():
            if issubclass(type(adapter), Repository) or issubclass(
                type(adapter), Service
            ):
                yield adapter

    def load_repositories(self):
        pass

    def load_internal_services(self):
        from fractal.core.event_sourcing.event_publisher import EventPublisher

        self.event_publisher = EventPublisher(self.load_event_projectors())

    def load_event_projectors(self):
        return []

    def load_ingress_services(self):
        pass

    def load_egress_services(self):
        pass

    def load_command_bus(self):
        from fractal.core.command_bus.command_bus import CommandBus

        self.command_bus = CommandBus()

    def install_repository(self, repository):
        self.repositories.append(repository)
        return repository

    def install_service(self, service, *, name=""):
        if not name:
            name = camel_to_snake(service.__name__)
        setattr(
            ApplicationContext, name, property(lambda self: next(service.install(self)))
        )
