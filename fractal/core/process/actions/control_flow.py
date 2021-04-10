from typing import Iterable, Optional

from fractal.core.process.action import Action
from fractal.core.process.process import Process
from fractal.core.process.process_scope import ProcessScope
from fractal.core.specifications.generic.specification import Specification


class IfElseAction(Action):
    def __init__(
        self,
        specification: Specification,
        process_true: Process,
        process_false: Optional[Process] = None,
    ):
        self.specification = specification
        self.process_true = process_true
        self.process_false = process_false

    def execute(self, scope: ProcessScope) -> ProcessScope:
        if self.specification.is_satisfied_by(scope):
            scope.update(self.process_true.run(scope))
        elif self.process_false:
            scope.update(self.process_false.run(scope))
        return scope


class WhileAction(Action):
    def __init__(self, specification: Specification, process: Process):
        self.specification = specification
        self.process = process

    def execute(self, scope: ProcessScope) -> ProcessScope:
        while self.specification.is_satisfied_by(scope):
            scope.update(self.process.run(scope))
        return scope


class ForEachAction(Action):
    def __init__(self, iterable: Iterable, process: Process):
        self.iterable = iterable
        self.process = process

    def execute(self, scope: ProcessScope) -> ProcessScope:
        for item in self.iterable:
            scope["item"] = item
            scope.update(self.process.run(scope))
        return scope
