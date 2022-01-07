import logging
import os
from typing import List, Tuple


class ApplicationContext(object):
    instance = None

    def __new__(cls, dotenv=True, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls, *args, **kwargs)
            if dotenv:
                from dotenv import load_dotenv

                load_dotenv()
            cls.instance.load()
        return cls.instance

    def load(self):
        from fractal.core.utils.loggers import init_logging

        init_logging(os.getenv("LOG_LEVEL", "INFO"))
        self.logger = logging.getLogger("app")
        self.repositories = []
        self.repository_names = []
        self.service_names = []

        self.load_internal_services()
        self.load_repositories()
        self.load_egress_services()

        from fractal.core.event_sourcing.event_publisher import EventPublisher

        self.event_publisher = EventPublisher(self.load_event_projectors())
        self.load_command_bus()
        self.load_ingress_services()

        for repository in self.repositories:
            assert repository.is_healthy()
        for service in self.services:
            assert service.is_healthy()

    def reload(self):
        self.load()

    def adapters(self):
        for repository in self.repositories:
            yield repository
        for service in self.services:
            yield service

    def load_internal_services(self):
        """Load services for internal use of the domain."""

    def load_repositories(self):
        """Load repositories for data access"""

    def load_egress_services(self):
        """Load services to external interfaces that are initiated by this service (outbound)"""

    def load_event_projectors(self):
        return []

    def load_command_bus(self):
        from fractal.core.command_bus.command_bus import CommandBus

        self.command_bus = CommandBus()

    def load_ingress_services(self):
        """Load services to external interfaces that are initiated by the external services (inbound)"""

    def install_repository(self, repository, *, name=""):
        if not name:
            from fractal.core.utils.string import camel_to_snake

            name = camel_to_snake(repository.__class__.__name__)
        self.repository_names.append(name)
        self.repositories.append(repository)
        return repository

    def install_service(self, service, *, name=""):
        if not name:
            from fractal.core.utils.string import camel_to_snake

            name = camel_to_snake(service.__name__)
        self.service_names.append(name)
        setattr(
            ApplicationContext, name, property(lambda self: next(service.install(self)))
        )

    @property
    def services(self):
        services = []
        for service_name in self.service_names:
            services.append(getattr(self, service_name))
        return services

    def get_parameters(self, parameters: List[str]) -> Tuple:
        for parameter in parameters:
            if not hasattr(self, parameter):
                from fractal import FractalException

                raise FractalException(
                    f"ApplicationContext does not provide '{parameter}'"
                )
        return tuple(getattr(self, p) for p in parameters)
