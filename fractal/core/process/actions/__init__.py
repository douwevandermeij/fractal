from typing import Optional

from fractal.core.process.action import Action
from fractal.core.process.process_scope import ProcessScope
from fractal.core.specifications.generic.specification import Specification


class SetValueAction(Action):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def execute(self, scope: ProcessScope) -> ProcessScope:
        return scope.update(ProcessScope(self.kwargs))


class IncreaseValueAction(Action):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def execute(self, scope: ProcessScope) -> ProcessScope:
        scope[self.name] += self.value
        return scope


class PrintAction(Action):
    def __init__(self, text):
        self.text = text

    def execute(self, scope: ProcessScope) -> ProcessScope:
        print(self.text)
        return scope


class PrintValueAction(Action):
    def __init__(self, name):
        self.name = name

    def execute(self, scope: ProcessScope) -> ProcessScope:
        print(scope[self.name])
        return scope


class AddEntityAction(Action):
    def __init__(self, repository_key: str = "repository", **entity_defaults):
        self.repository_key = repository_key
        self.entity_defaults = entity_defaults

    def execute(self, scope: ProcessScope) -> ProcessScope:
        entity_class = scope[self.repository_key].entity
        data = self.entity_defaults
        if hasattr(scope, "contract"):
            data.update(scope["contract"])
        entity = entity_class(**data)
        scope["entity"] = scope[self.repository_key].add(entity)
        return scope


class UpdateEntityAction(Action):
    def __init__(self, repository_key: str = "repository"):
        self.repository_key = repository_key

    def execute(self, scope: ProcessScope) -> ProcessScope:
        entity = scope["entity"].update(scope["contract"])
        scope["entity"] = scope[self.repository_key].update(entity)
        return scope


class FetchEntityAction(Action):
    def __init__(
        self, specification: Specification, repository_key: str = "repository"
    ):
        self.specification = specification
        self.repository_key = repository_key

    def execute(self, scope: ProcessScope) -> ProcessScope:
        scope["entity"] = scope[self.repository_key].find_one(self.specification)
        return scope


class FindEntitiesAction(Action):
    def __init__(
        self,
        specification: Optional[Specification] = None,
        repository_key: str = "repository",
    ):
        self.specification = specification
        self.repository_key = repository_key

    def execute(self, scope: ProcessScope) -> ProcessScope:
        scope["entities"] = scope["entity"] = scope[self.repository_key].find(
            self.specification
        )
        return scope


class DeleteEntityAction(Action):
    def __init__(
        self, specification: Specification, repository_key: str = "repository"
    ):
        self.specification = specification
        self.repository_key = repository_key

    def execute(self, scope: ProcessScope) -> ProcessScope:
        scope[self.repository_key].remove_one(self.specification)
        return scope
