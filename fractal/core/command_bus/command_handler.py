from abc import ABC, abstractmethod
from typing import List, Type

from fractal.core.command_bus.command import Command


class CommandHandler(ABC):
    @abstractmethod
    def commands(self) -> List[Type[Command]]:
        """Returns list of commands that this handler can handle."""

    @abstractmethod
    def handle(self, command: Command):
        """Handle command, might return a value."""
