from abc import ABC

from fractal.core.process.process_scope import ProcessScope


class Action(ABC):
    def execute(self, scope: ProcessScope) -> ProcessScope:
        """Execute the action"""
