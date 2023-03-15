from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from fractal.core.command_bus.command import Command

_Command = TypeVar("_Command", bound=Command)


class CommandHandler(Generic[_Command], ABC):
    command: Type[_Command] = None

    @abstractmethod
    def handle(self, command: _Command):
        """Handle command, might return a value."""
