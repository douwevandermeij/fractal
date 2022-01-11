from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

Command = TypeVar("Command")


class CommandHandler(Generic[Command], ABC):
    command: Type[Command] = None

    @abstractmethod
    def handle(self, command: Command):
        """Handle command, might return a value."""
