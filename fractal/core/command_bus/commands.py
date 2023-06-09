from dataclasses import dataclass
from typing import Generic

from fractal_repositories.core.repositories import EntityType
from fractal_specifications.generic.specification import Specification

from fractal.core.command_bus.command import Command


@dataclass
class AddEntityCommand(Generic[EntityType], Command):
    entity: EntityType
    specification: Specification


@dataclass
class UpdateEntityCommand(Generic[EntityType], Command):
    id: str
    entity: EntityType
    specification: Specification


@dataclass
class DeleteEntityCommand(Generic[EntityType], Command):
    specification: Specification
