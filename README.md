# Fractal

> Fractal is a scaffolding toolkit for building SOLID logic for your Python applications.

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]
[![Code Quality][quality-image]][quality-url]

<!-- Badges -->

[pypi-image]: https://img.shields.io/pypi/v/fractal-toolkit
[pypi-url]: https://pypi.org/project/fractal-toolkit/
[build-image]: https://github.com/douwevandermeij/fractal/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/douwevandermeij/fractal/actions/workflows/build.yml
[coverage-image]: https://codecov.io/gh/douwevandermeij/fractal/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/douwevandermeij/fractal
[quality-image]: https://api.codeclimate.com/v1/badges/55adbc041d119d371ef7/maintainability
[quality-url]: https://codeclimate.com/github/douwevandermeij/fractal

## Installation

```sh
pip install fractal-toolkit
```

## Upgrading

### From 0.x to 1.x

Alter the FastAPI installation in `app/main.py` from:
```python
fractal = ApplicationFractal()

app = install_fastapi(fractal.settings)
```

To:
```python
fractal = ApplicationFractal()

from app.roles import RolesService

fractal.context.install_service(RolesService, name="roles_service")

app = install_fastapi(fractal.settings)
```

Add `app/roles.py` containing:
```python
from fractal.contrib.roles.models import Role
from fractal.contrib.roles.services import BaseRolesService


class Admin(Role):
    ...


class User(Role):
    ...


class RolesService(BaseRolesService):
    def __init__(self):
        self.roles = [Admin(), User()]
```

Add `entities_endpoint` and `entity_endpoint` to `BasicRestRouterService` subclasses. Name them similar to the routes. Example:
```python
class GroupRouterService(BasicRestRouterService):
    entities_route = Routes.GROUPS
    entity_route = Routes.GROUP
    entities_endpoint = "GROUPS"
    entity_endpoint = "GROUP"
```

Another solution is to use a helper function:
```python
class GroupRouterService(BasicRestRouterService):
    entities_route = Routes.GROUPS
    entity_route = Routes.GROUP
    entities_endpoint = Routes.name_by_route(Routes.GROUPS)
    entity_endpoint = Routes.name_by_route(Routes.GROUP)
```

But then the `Routes` class also needs to be extended:
```python
import functools
import inspect


class Routes:
    @staticmethod
    @functools.cache
    def names_by_route():
        return {v: k for k, v in inspect.getmembers(Routes) if not k.startswith("_")}

    @staticmethod
    @functools.cache
    def name_by_route(endpoint: str):
        return Routes.names_by_route().get(endpoint)

    ...
```

For manual routes, alter:
```python
payload: TokenPayloadRoles = Depends(
    get_payload_roles(fractal, roles=roles.get("get", ["user"]))
)
```

To:
```python
payload: TokenPayloadRoles = Depends(
    get_payload_roles(
        fractal,
        endpoint=router_service_class().entities_endpoint,
        method="get",
    )
)
```

Also alter the body of the manual routes to include `specification=payload.specification`, like:
```python
def get_entity(...):
    return router_service_class().get_entity(
        entity_id=entity_id,
        specification=payload.specification,
        **payload.dict(),
    )
```

The router service should forward the specification to the ingress service:
```python
class GroupRouterService(BasicRestRouterService):
    ...
    def get_entity(
        self,
        entity_id: UUID,
        specification: Specification = None,
        **kwargs,
    ):
        return self.ingress_service.get(str(entity_id), str(kwargs.get("account")), specification=specification)
```

Ingress services need to accept a specification as parameter and use it:
```python
@ApplicationContext.register_ingress_service("group_service")
class GroupService(Service):
    ...
    def get(
        self,
        entity_id: str,
        account_id: str,
        *,
        specification: Specification = None,
    ):
        entity = self.group_repository.find_one(specification.And(IdSpecification(entity_id)))
        self._enrich_expense(entity)
        return entity
```

This holds for all functions of the router service and the ingress service.
Furthermore, the original specifications inside the services and/or commands can be adjusted accordingly.
Before doing that, the specification needs to be passed into the commands:
```python
@ApplicationContext.register_ingress_service("group_service")
class GroupService(Service):
    ...
    def add(...):
        self.command_bus.handle(
            AddGroupCommand(
                user_id=user_id,
                entity=entity,
                specification=specification,
            ),
        )

    def update(...):
        self.command_bus.handle(
            UpdateGroupCommand(
                id=entity_id,
                entity=entity,
                user_id=user_id,
                specification=specification,
            ),
        )
```

As an example, the `AddEntityCommand` and `UpdateEntityCommand` can verify the data that is modified in the repository with:
```python
    ...
    if command.specification:
        command.specification.is_satisfied_by(command.entity)
    self.group_repository.add(command.entity)
```

## Usage

* Fractal can be used inside large Python applications to isolate certain (logical related) behaviour from the rest of
the application.
* Fractal is ideal for refactoring large applications into smaller parts
* Fractal applications by design are microservices
  * Just wrap the app in an HTTP framework (like FastAPI, see contrib module) and expose with Docker
  * Other usages apart from HTTP (and Docker) are also possible
    * Like subscribing to a data stream or pub/sub channel

## Architecture

Applications that use Fractal can be built in many ways, including a non-SOLID architecture.
The Fractal toolkit tries to make it easier to go for the SOLID approach.

To start a Fractal project, the first class to make derives from `fractal.Fractal`.
It should provide a `fractal.core.utils.settings.Settings` object and a 
`fractal.core.utils.application_context.ApplicationContext` object, which should also be derived from.

The `Settings` class provides all static configuration for the application; it's the place where environment variables
are loaded. The class creates a singleton object.

The `Context` class provides the dynamic configuration of the application, using the `Settings` object.
In the `Context` all dependencies will be injected.

### Hexagonal Architecture (ports and adapters)

In Hexagonal Architecture, together with Domain Driven Design principles, the core of the application, is the bounded
context containing the domain objects (entities, repositories, services, etc.) but without specific implementation
details. Just the domain logic. From now on we call the core the domain.

This is (loosely) enforced by not allowing dependencies to external packages inside the domain.
This, in turn, is the _dependency inversion principle_ of SOLID.

The repositories and services inside the domain are interfaces or abstract classes. These are known as ports.

Next to the domain there are the adapters. Each interface or port needs an adapter to function at runtime. Adapters are
allowed to depend on external packages.

At runtime, in the application `Context`, based on `Settings`, the appropriate adapter will be set for each port.

### Basic application structure

A typical application folder structure using Fractal looks like:

    app/
    ├── adapters/
    │   ├── __init__.py
    │   └── products.py
    ├── domain/
    │   ├── __init__.py
    │   └── products.py
    ├── context.py
    ├── main.py
    └── settings.py

With this, a fully functional Fractal application can be built having a Python interface. That is, the logic of the
application can only be reached by invoking methods on Python level.

Such Fractal applications might be used as part of larger (Python) applications to isolate or encapsulate certain
behaviour. The larger application itself can also be a Fractal application, and so on. Hence the name: Fractal.

While using Fractal as a way to have separation of concerns with separate isolated bounded contexts in Python
applications, it's also possible to wrap Fractal in a small application and expose as REST API using, for example,
FastAPI, Flask or Django. Next that application can be deployed again in a Docker environment. This makes Fractal a
perfect fit for microservices as well.

As a rule of thumb, continuing on the separation of concerns, the folder/file structure inside a Fractal application
should follow the naming of the subject (rather than the naming of the responsibilities of module).
In the example app this is denoted by `products.py` in both the `domain` folder as the `adapters` folder.
When the file is getting too big to be easily readable or maintainable, it can be converted into a package.
Within the package the files can be named by their responsibilities.

An example package folder structure:

    app/
    ├── adapters/
    │   └── products/
    │       ├── __init__.py
    │       ├── django.py
    │       └── fastapi.py
    ├── domain/
    │   └── products/
    │       ├── __init__.py
    │       ├── commands/
    │       │   ├── __init__.py
    │       │   └── add.py
    │       └── events.py
    ├── context.py
    ├── main.py
    └── settings.py

As can be seen in the example package folder structure, in the `domain` the package contains files about certain
actions or responsibilities andf in the `adapters` folder it's more about the target implementation.
Of course the target implementation file can be converted into a package again and contain files for certain
responsibilities again.

#### Example file contents

##### main.py

```python
from fractal import Fractal

from app.context import ApplicationContext
from app.settings import Settings


class ApplicationFractal(Fractal):
    settings = Settings()
    context = ApplicationContext()
```

##### settings.py

```python
import os

from fractal.core.utils.settings import Settings as BaseSettings


class Settings(BaseSettings):
    BASE_DIR = os.path.dirname(__file__)
    ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
    APP_NAME = os.getenv("APP_NAME", "product_system")

    def load(self):
        self.PRODUCT_REPOSITORY_BACKEND = os.getenv("PRODUCT_REPOSITORY_BACKEND", "")
```

##### context.py

```python
from fractal.core.utils.application_context import ApplicationContext as BaseContext

from app.settings import Settings


class ApplicationContext(BaseContext):
    def load_repositories(self):
        from app.domain.products import ProductRepository
      
        if Settings().PRODUCT_REPOSITORY_BACKEND == "sql":
            '''example: some sql adapter code'''
        elif Settings().PRODUCT_REPOSITORY_BACKEND == "file":
            '''example: some file adapter code'''
        else:
            from app.adapters.products import InMemoryProductRepository

            self.product_repository: ProductRepository = self.install_repository(
                InMemoryProductRepository(),
            )
```

##### domain/products.py

```python
from abc import ABC
from dataclasses import dataclass

from fractal.core.models import Model
from fractal.core.repositories import Repository


@dataclass
class Product(Model):
    id: str
    name: str


class ProductRepository(Repository[Product], ABC):
    pass
```

##### adapters/products.py

```python
from fractal.core.repositories.inmemory_repository_mixin import InMemoryRepositoryMixin

from app.domain.products import Product, ProductRepository


class InMemoryProductRepository(ProductRepository, InMemoryRepositoryMixin[Product]):
    pass
```

## Advanced features

### Command bus pattern

A command is a container to invoke actions in the domain, from inside and outside of the domain.
A command has a one-to-one relation with a command handler.
The command handler can be seen as a single transaction, e.g., to a database.

The code in the command handler should just be doing just the things that are necessary to be inside the transaction.
Transactions can fail, so it's important to prevent side effects from happening and include only the code that needs to
go in the same transaction and thus will be rolled back as a whole in case the transaction fails.

Secondary actions that need to take place _after_ the action has been done, should be outside of scope of the command
handler.

After a command handler has been completed successfully, that is, when the transaction is persisted, an event can be
published. This event is the trigger for all secondary actions, which in turn can be commands again.

#### Example file contents

The affected files in the folder structure:

    app/
    └── domain/
    │   └── products/
    │       └── commands.py
    └── context.py

##### commands.py

Without publishing events:

```python
from dataclasses import dataclass

from fractal.core.command_bus.command_handler import CommandHandler
from fractal.core.command_bus.commands import AddEntityCommand

from app.context import ApplicationContext
from app.domain.products import Product, ProductRepository


@dataclass
class AddProductCommand(AddEntityCommand[Product]):
    pass


class AddProductCommandHandler(CommandHandler):
    command = AddProductCommand

    def __init__(
        self,
        product_repository: ProductRepository,
    ):
        self.product_repository = product_repository

    @staticmethod
    def install(context: ApplicationContext):
        context.command_bus.add_handler(
            AddProductCommandHandler(
                context.product_repository,
            )
        )

    def handle(self, command: AddProductCommand):
        self.product_repository.add(command.entity)
```

##### context.py

```python
from fractal.core.utils.application_context import ApplicationContext as BaseContext


class ApplicationContext(BaseContext):
  
    ...
    
    def load_command_bus(self):
        super(ApplicationContext, self).load_command_bus()

        from app.domain.products.commands import AddProductCommandHandler

        AddProductCommandHandler.install(self)
```

### Event publishing

When an event gets published, the `EventPublisher` will iterate over its registered projectors (`EventProjector`).
Each projector will be invoked with the event as a parameter.

Projectors can do anything:
- printing the event to the console
- populating a repository
  - like an event store
  - or a read optimized view
- invoking a new command
- sending the event to an external service, which may:
  - invoke a new command
  - send an email

Each projector should only be doing one thing.
The relation between an event and a projector is one-to-many.

**!! CAVEAT !!**

When using events, and especially when sending events to an external service, be aware that these other services might
have a dependency on the structure of the event.
Changing existing events is **dangerous**.
The best approach here is to apply the _open-closed principle_ of SOLID, open for extension, closed for modification.
Alternatively creating a new event is also possible.

#### Example file contents

The affected files in the folder structure, on top of the command bus pattern code:

    app/
    └── domain/
    │   └── products/
    │       ├── commands.py
    │       └── events.py
    └── context.py

##### commands.py

```python
from dataclasses import dataclass
from datetime import datetime

from fractal.core.command_bus.command_handler import CommandHandler
from fractal.core.command_bus.commands import AddEntityCommand
from fractal.core.event_sourcing.event_publisher import EventPublisher

from app.context import ApplicationContext
from app.domain.products import Product, ProductRepository
from app.domain.products.events import ProductAddedEvent


@dataclass
class AddProductCommand(AddEntityCommand[Product]):
    user_id: str


class AddProductCommandHandler(CommandHandler):
    command = AddProductCommand

    def __init__(
        self,
        event_publisher: EventPublisher,
        product_repository: ProductRepository,
    ):
        self.event_publisher = event_publisher
        self.product_repository = product_repository

    @staticmethod
    def install(context: ApplicationContext):
        context.command_bus.add_handler(
            AddProductCommandHandler(
                context.event_publisher,
                context.product_repository,
            )
        )

    def handle(self, command: AddProductCommand):
        event = ProductAddedEvent(
            id=command.entity.id,
            name=command.entity.name,
            created_by=command.user_id,
            created_on=datetime.utcnow(),
        )
        self.product_repository.add(command.entity)
        self.event_publisher.publish_event(event)
```

##### events.py

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Type

from fractal.core.command_bus.command import Command
from fractal.core.event_sourcing.event import (
    BasicSendingEvent,
    Event,
    EventCommandMapper,
)


@dataclass
class ProductEvent(BasicSendingEvent):
    id: str

    @property
    def object_id(self):
        return self.id

    @property
    def aggregate_root_id(self):
        return self.id


@dataclass
class ProductAddedEvent(ProductEvent):
    name: str
    created_by: str
    created_on: datetime


class ProductEventCommandMapper(EventCommandMapper):
    def mappers(self) -> Dict[Type[Event], List[Callable[[Event], Command]]]:
        return {
            # example:
            # ProductAddedEvent: [
            #     lambda event: SomeCommand(...)
            # ],
        }
```

##### context.py

```python
from fractal.core.utils.application_context import ApplicationContext as BaseContext


class ApplicationContext(BaseContext):
  
    ...
    
    def load_event_projectors(self):
        from fractal.core.event_sourcing.projectors.command_bus_projector import (
            CommandBusProjector,
        )

        from app.domain.products.events import ProductEventCommandMapper

        self.command_bus_projector = CommandBusProjector(
            lambda: self.command_bus,
            [
                ProductEventCommandMapper(),
            ],
        )

        from fractal.core.event_sourcing.projectors.print_projector import (
            PrintEventProjector,
        )

        return [
            self.command_bus_projector,
            PrintEventProjector(),
        ]
```

### Eventual consistency

TODO

### Event sourcing

TODO

### Specification pattern

TODO

### FastAPI + Docker

TODO

Request contract, together with URI parameters and authentication token payload can be processed by the application
by using the command bus. The command can ingest the separate variables and/or domain objects (entities).

Response contract might be different from the domain object that is affected by the request.

### Authentication

TODO
