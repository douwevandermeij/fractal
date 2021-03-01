from collections import defaultdict
from typing import List, Type

from fractal.core.command_bus.command import Command
from fractal.core.command_bus.command_handler import CommandHandler


class CommandBus(CommandHandler):
    def __init__(self):
        self.handlers = defaultdict(list)

    def commands(self) -> List[Type[Command]]:
        return []

    def set_handlers(self, handlers: List[CommandHandler]):
        for handler in handlers:
            for command in handler.commands():
                self.handlers[command.__name__].append(handler)

    def add_handler(self, handler: CommandHandler):
        for command in handler.commands():
            self.handlers[command.__name__].append(handler)

    def handle(self, command: Command):
        ret = {}
        for handler in self.handlers[command.__class__.__name__]:
            res = handler.handle(command)
            if res is not None:
                ret[handler.__class__.__name__] = res
        return ret
