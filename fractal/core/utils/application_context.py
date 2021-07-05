import logging
import os
from io import StringIO
from typing import List, Tuple

from dotenv import load_dotenv

from fractal import FractalException
from fractal.core.event_sourcing.event_publisher import EventPublisher
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
        self.services = []

        self.load_internal_services()
        self.load_repositories()
        self.load_egress_services()
        self.event_publisher = EventPublisher(self.load_event_projectors())
        self.load_command_bus()
        self.load_ingress_services()

        for repository in self.repositories:
            repository.is_healthy()
        for service_name in self.services:
            getattr(self, service_name).is_healthy()

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
        pass

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
        self.services.append(name)
        setattr(
            ApplicationContext, name, property(lambda self: next(service.install(self)))
        )

    def get_parameters(self, parameters: List[str]) -> Tuple:
        for parameter in parameters:
            if not hasattr(self, parameter):
                raise FractalException(
                    f"ApplicationContext does not provide '{parameter}'"
                )
        return tuple(getattr(self, p) for p in parameters)
