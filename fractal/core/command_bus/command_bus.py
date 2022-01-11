from collections import defaultdict
from typing import List

from fractal.core.command_bus.command import Command
from fractal.core.command_bus.command_handler import CommandHandler


class CommandBus:
    def __init__(self):
        self.handlers = defaultdict(list)

    def set_handlers(self, handlers: List[CommandHandler]):
        for handler in handlers:
            self.add_handler(handler)

    def add_handler(self, handler: CommandHandler):
        self.handlers[handler.command.__name__].append(handler)

    async def handle_async(self, command: Command):
        ret = {}
        for handler in self.handlers[command.__class__.__name__]:
            res = await handler.handle(command)
            if res is not None:
                ret[handler.__class__.__name__] = res
        return ret

    def handle(self, command: Command):
        ret = {}
        for handler in self.handlers[command.__class__.__name__]:
            res = handler.handle(command)
            if res is not None:
                ret[handler.__class__.__name__] = res
        return ret
