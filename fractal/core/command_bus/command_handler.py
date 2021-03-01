from abc import ABC, abstractmethod
from typing import List, Type

from fractal.core.command_bus.command import Command


class CommandHandler(ABC):
    @abstractmethod
    def commands(self) -> List[Type[Command]]:
        pass

    @abstractmethod
    def handle(self, command: Command):
        pass
