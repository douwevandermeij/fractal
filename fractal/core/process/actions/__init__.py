from typing import Callable, Optional

from fractal_specifications.generic.specification import Specification

from fractal.core.process.action import Action
from fractal.core.process.process_scope import ProcessScope


class SetValueAction(Action):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def execute(self, scope: ProcessScope) -> ProcessScope:
        return scope.update(ProcessScope(self.kwargs))


class ApplyToValueAction(Action):
    def __init__(self, *, field: str, function: Callable):
        self.field = field
        self.function = function

    def execute(self, scope: ProcessScope) -> ProcessScope:
        scope[self.field] = self.function(scope[self.field])
        return scope


class IncreaseValueAction(Action):
    def __init__(self, *, field: str, value):
        self.field = field
        self.value = value

    def execute(self, scope: ProcessScope) -> ProcessScope:
        scope[self.field] += self.value
        return scope


class PrintAction(Action):
    def __init__(self, *, text):
        self.text = text

    def execute(self, scope: ProcessScope) -> ProcessScope:
        print(self.text)
        return scope


class PrintValueAction(Action):
    def __init__(self, *, field: str):
        self.field = field

    def execute(self, scope: ProcessScope) -> ProcessScope:
        print(scope[self.field])
        return scope


class AddEntityAction(Action):
    def __init__(self, *, repository_name: str, entity: str = "entity"):
        self.repository_name = repository_name
        self.entity = entity

    def execute(self, scope: ProcessScope) -> ProcessScope:
        repository = getattr(scope.fractal.context, self.repository_name)
        repository.add(getattr(scope, self.entity))
        return scope


class UpdateEntityAction(Action):
    def __init__(
        self, *, repository_name: str, entity: str = "entity", upsert: bool = False
    ):
        self.repository_name = repository_name
        self.entity = entity
        self.upsert = upsert

    def execute(self, scope: ProcessScope) -> ProcessScope:
        repository = getattr(scope.fractal.context, self.repository_name)
        repository.update(getattr(scope, self.entity), self.upsert)
        return scope


class FetchEntityAction(Action):
    def __init__(
        self,
        *,
        repository_name: str,
        specification: Specification,
        entity: str = "entity",
    ):
        self.repository_name = repository_name
        self.specification = specification
        self.entity = entity

    def execute(self, scope: ProcessScope) -> ProcessScope:
        repository = getattr(scope.fractal.context, self.repository_name)
        scope[self.entity] = repository.find_one(self.specification)
        return scope


class FindEntitiesAction(Action):
    def __init__(
        self,
        *,
        repository_name: str,
        specification: Optional[Specification] = None,
        entities: str = "entities",
    ):
        self.repository_name = repository_name
        self.specification = specification
        self.entities = entities

    def execute(self, scope: ProcessScope) -> ProcessScope:
        repository = getattr(scope.fractal.context, self.repository_name)
        scope[self.entities] = repository.find(self.specification)
        return scope


class DeleteEntityAction(Action):
    def __init__(self, *, repository_name: str, specification: Specification):
        self.repository_name = repository_name
        self.specification = specification

    def execute(self, scope: ProcessScope) -> ProcessScope:
        repository = getattr(scope.fractal.context, self.repository_name)
        repository.remove_one(self.specification)
        return scope
