from dataclasses import dataclass
from typing import Generic

from fractal_specifications.generic.specification import Specification

from fractal.core.command_bus.command import Command
from fractal.core.repositories import Entity


@dataclass
class AddEntityCommand(Generic[Entity], Command):
    entity: Entity
    specification: Specification


@dataclass
class UpdateEntityCommand(Generic[Entity], Command):
    id: str
    entity: Entity
    specification: Specification


@dataclass
class DeleteEntityCommand(Generic[Entity], Command):
    specification: Specification
