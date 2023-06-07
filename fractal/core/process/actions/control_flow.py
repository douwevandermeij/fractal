from typing import Iterable, List, Optional

from fractal_specifications.generic.specification import Specification

from fractal.core.process.action import Action
from fractal.core.process.process import Process
from fractal.core.process.process_scope import ProcessScope


class IfElseAction(Action):
    def __init__(
        self,
        specification: Specification,
        actions_true: List[Action],
        actions_false: Optional[List[Action]] = None,
    ):
        self.specification = specification
        self.process_true = Process(actions_true)
        self.process_false = Process(actions_false) if actions_false else None

    def execute(self, scope: ProcessScope) -> ProcessScope:
        if self.specification.is_satisfied_by(scope):
            scope.update(self.process_true.run(scope))
        elif self.process_false:
            scope.update(self.process_false.run(scope))
        return scope


class WhileAction(Action):
    def __init__(self, specification: Specification, actions: List[Action]):
        self.specification = specification
        self.process = Process(actions)

    def execute(self, scope: ProcessScope) -> ProcessScope:
        while self.specification.is_satisfied_by(scope):
            scope.update(self.process.run(scope))
        return scope


class ForEachAction(Action):
    def __init__(self, iterable: Iterable, actions: List[Action]):
        self.iterable = iterable
        self.process = Process(actions)

    def execute(self, scope: ProcessScope) -> ProcessScope:
        for item in self.iterable:
            scope["item"] = item
            scope.update(self.process.run(scope))
        return scope
