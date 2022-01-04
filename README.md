# Fractal

> Fractal is a scaffolding toolkit for building SOLID logic for your Python applications.

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]
[![Code Quality][quality-image]][quality-url]

## Installation

```sh
pip install fractal-toolkit
```

<!-- Badges -->

[pypi-image]: https://img.shields.io/pypi/v/fractal-toolkit
[pypi-url]: https://pypi.org/project/fractal-toolkit/
[build-image]: https://github.com/douwevandermeij/fractal/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/douwevandermeij/fractal/actions/workflows/build.yml
[coverage-image]: https://codecov.io/gh/douwevandermeij/fractal/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/douwevandermeij/fractal
[quality-image]: https://api.codeclimate.com/v1/badges/55adbc041d119d371ef7/maintainability
[quality-url]: https://codeclimate.com/github/douwevandermeij/fractal

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
    │   └── users.py
    ├── domain/
    │   └── users.py
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

#### Example file contents

##### main.py

```python
from app.service.context import ApplicationContext
from app.service.settings import Settings
from fractal import Fractal


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
    APP_NAME = os.getenv("APP_NAME", "user_system")

    def load(self):
        self.USER_REPOSITORY_BACKEND = os.getenv("USER_REPOSITORY_BACKEND", "")
```

##### context.py

```python
from app.service.settings import Settings
from fractal.core.utils.application_context import ApplicationContext as BaseContext


class ApplicationContext(BaseContext):
    def load_repositories(self):
        if Settings().USER_REPOSITORY_BACKEND == "sql":
            '''some sql adapter code'''
        elif Settings().USER_REPOSITORY_BACKEND == "file":
            '''some file adapter code'''
        else:
            from app.service.adapters.users import InMemoryUserRepository

            self.user_repository: UserRepository = self.install_repository(
                InMemoryUserRepository(),
            )
```

##### domain/users.py

```python
from abc import ABC
from dataclasses import dataclass  # NOQA

from pydantic.dataclasses import dataclass

from fractal.core.exceptions import DomainException
from fractal.core.models import Model
from fractal.core.repositories import Repository


@dataclass
class User(Model):
    id: str
    name: str


class UserNotFoundException(DomainException):
    code = "USER_NOT_FOUND"
    status_code = 404

    def __init__(self, message=None):
        if not message:
            message = "User not found!"
        super(UserNotFoundException, self).__init__(message)


class UserRepository(Repository[User], ABC):
    entity = User
```

##### adapters/users.py

```python
from app.service.domain.users import (
    User,
    UserNotFoundException,
    UserRepository,
)
from fractal.core.repositories.inmemory_repository_mixin import InMemoryRepositoryMixin
from fractal.core.specifications.generic.specification import Specification


class InMemoryUserRepository(UserRepository, InMemoryRepositoryMixin[User]):
    def find_one(self, specification: Specification) -> User:
        obj = super(InMemoryUserRepository, self).find_one(specification)
        if not obj:
            raise UserNotFoundException
        return obj
```

### Advanced features

#### Command pattern

TODO

#### Specification pattern

TODO

#### FastAPI + Docker

TODO

#### Authentication

TODO

#### Event sourcing

TODO
