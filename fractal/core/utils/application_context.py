import logging
import os
from types import FunctionType
from typing import List, Tuple


class ApplicationContext(object):
    instance = None
    settings = None
    registered_repositories = []
    registered_command_handlers = []
    registered_ingress_services = []
    registered_egress_services = []
    registered_internal_services = []

    def __new__(cls, dotenv=True, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls, *args, **kwargs)
            if dotenv:
                from dotenv import load_dotenv

                load_dotenv()
            cls.instance.load()
        return cls.instance

    def __getattr__(self, item):
        return None

    @classmethod
    def register_repository(cls, name):
        setattr(cls, name, None)

        def inner(select_repository):
            cls.registered_repositories.append((name, select_repository))

        return inner

    @classmethod
    def register_command_handler(cls, command_handler):
        cls.registered_command_handlers.append(command_handler)
        return command_handler

    @classmethod
    def register_ingress_service(cls, name):
        def inner(service):
            cls.registered_ingress_services.append((name, service))

        return inner

    @classmethod
    def register_egress_service(cls, name):
        def inner(service):
            cls.registered_egress_services.append((name, service))

        return inner

    @classmethod
    def register_internal_service(cls, name):
        def inner(service):
            cls.registered_internal_services.append((name, service))

        return inner

    def load(self):
        from fractal.core.utils.loggers import init_logging

        init_logging(os.getenv("LOG_LEVEL", "INFO"))
        self.logger = logging.getLogger("app")
        self.repositories = set()
        self.repository_names = set()
        self.service_names = set()
        self.load_internal_services()
        self.load_repositories()
        self.load_egress_services()
        self.load_event_publisher()
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
        for name, service in self.registered_internal_services:
            _service = self.install_service(
                service(self.settings)
                if isinstance(service, FunctionType)
                else service,
                name=name,
            )
            setattr(self, name, _service())

    def load_repositories(self):
        """Load repositories for data access"""
        for name, repository in self.registered_repositories:
            setattr(
                self,
                name,
                self.install_repository(
                    repository(self.settings)
                    if isinstance(repository, FunctionType)
                    else repository,
                    name=name,
                ),
            )
        self.load_event_store()

    def load_event_store(self):
        if (
            hasattr(self.settings, "EVENT_STORE_BACKEND")
            and self.settings.EVENT_STORE_BACKEND == "firestore"
        ):
            from fractal.contrib.gcp.firestore.event_store import (
                FirestoreEventStoreRepository,
            )
            from fractal.core.event_sourcing.event_store import EventStoreRepository

            kwargs = {}
            if app_name := getattr(self.settings, "APP_NAME"):
                kwargs["collection_prefix"] = app_name

            self.event_store_repository: EventStoreRepository = (
                FirestoreEventStoreRepository(**kwargs)
            )

            from fractal.contrib.fastapi.utils.json_encoder import (
                BaseModelEnhancedEncoder,
            )
            from fractal.core.event_sourcing.event import BasicSendingEvent
            from fractal.core.event_sourcing.event_store import (
                EventStore,
                JsonEventStore,
            )
            from fractal.core.utils.subclasses import all_subclasses

            self.event_store: EventStore = JsonEventStore(
                event_store_repository=self.event_store_repository,
                events=all_subclasses(BasicSendingEvent),
                json_encoder=BaseModelEnhancedEncoder,
            )
        else:
            from fractal.core.event_sourcing.event_store import (
                EventStoreRepository,
                InMemoryEventStoreRepository,
            )

            self.event_store_repository: EventStoreRepository = (
                InMemoryEventStoreRepository()
            )

            from fractal.core.event_sourcing.event_store import (
                EventStore,
                ObjectEventStore,
            )

            self.event_store: EventStore = ObjectEventStore(
                event_store_repository=self.event_store_repository,
            )

    def load_egress_services(self):
        """Load services to external interfaces that are initiated by this service (outbound)"""
        for name, service in self.registered_egress_services:
            _service = self.install_service(
                service(self.settings)
                if isinstance(service, FunctionType)
                else service,
                name=name,
            )
            setattr(self, name, _service())

    def load_event_publisher(self):
        from fractal.core.event_sourcing.event_publisher import EventPublisher

        self.event_publisher = EventPublisher(self.load_event_projectors())

    def load_event_projectors(self):
        from fractal.core.event_sourcing.event import EventCommandMapper
        from fractal.core.event_sourcing.projectors.command_bus_projector import (
            CommandBusProjector,
        )
        from fractal.core.utils.subclasses import all_subclasses

        projectors = []

        if getattr(self.settings, "EVENT_STORE_PROJECTOR", None):
            from fractal.core.event_sourcing.projectors.event_store_projector import (
                EventStoreProjector,
            )

            projectors.append(EventStoreProjector(self.event_store))

        if getattr(self.settings, "PRINT_PROJECTOR", None):
            from fractal.core.event_sourcing.projectors.print_projector import (
                PrintEventProjector,
            )

            projectors.append(PrintEventProjector())

        if gcp_project_id := getattr(self.settings, "GCP_PROJECT_ID", None):
            from fractal.contrib.gcp.pubsub.projectors import PubSubEventBusProjector

            projectors.append(
                PubSubEventBusProjector(
                    project_id=gcp_project_id,
                    topic=getattr(self.settings, "GCP_PUBSUB_TOPIC", ""),
                ),
            )

        # First process all notifiers/emitters/persistency before chaining commands (and projecting new events)
        self.command_bus_projector = CommandBusProjector(
            lambda: self.command_bus,
            all_subclasses(EventCommandMapper),
        )
        projectors.append(self.command_bus_projector)

        return projectors

    def load_command_bus(self):
        from fractal.core.command_bus.command_bus import CommandBus

        self.command_bus = CommandBus()

        for handler in self.registered_command_handlers:
            handler.install(self)

    def load_ingress_services(self):
        """Load services to external interfaces that are initiated by the external services (inbound)"""
        for name, service in self.registered_ingress_services:
            _service = self.install_service(
                service(self.settings)
                if isinstance(service, FunctionType)
                else service,
                name=name,
            )
            setattr(self, name, _service())

    def install_repository(self, repository, *, name=""):
        if not name:
            from fractal.core.utils.string import camel_to_snake

            name = camel_to_snake(repository.__class__.__name__)
        self.repository_names.add(name)
        self.repositories.add(repository)
        return repository

    def install_service(self, service, *, name=""):
        if not name:
            from fractal.core.utils.string import camel_to_snake

            name = camel_to_snake(service.__name__)
        self.service_names.add(name)
        _service = service.install(self)
        setattr(ApplicationContext, name, lambda self: next(_service))
        return lambda: next(_service)

    @property
    def services(self):
        for service_name in self.service_names:
            service = getattr(self, service_name)
            if callable(service):
                service = service()
                setattr(self, service_name, service)
            yield service

    def get_parameters(self, parameters: List[str]) -> Tuple:
        for parameter in parameters:
            if not hasattr(self, parameter):
                from fractal import FractalException

                raise FractalException(
                    f"ApplicationContext does not provide '{parameter}'"
                )
        return tuple(getattr(self, p) for p in parameters)
