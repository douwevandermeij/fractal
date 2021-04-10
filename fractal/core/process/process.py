from typing import List, Optional

from fractal.core.process.action import Action
from fractal.core.process.process_scope import ProcessScope


class Process:
    def __init__(self, actions: List[Action]):
        self.actions = actions

    def run(self, scope: Optional[ProcessScope] = None) -> ProcessScope:
        if not scope:
            scope = ProcessScope()
        for action in self.actions:
            scope.update(action.execute(scope))
        return scope
