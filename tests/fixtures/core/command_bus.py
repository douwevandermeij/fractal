import pytest


@pytest.fixture
def command_bus():
    from fractal.core.command_bus.command_bus import CommandBus

    return CommandBus()


@pytest.fixture
def command():
    from fractal.core.command_bus.command import Command

    return Command()


@pytest.fixture
def command_handler(command):
    from fractal.core.command_bus.command import Command
    from fractal.core.command_bus.command_handler import CommandHandler

    class FakeCommandHandler(CommandHandler):
        def __init__(self):
            self.command = type(command)

        def handle(self, command: Command):
            return 1

    return FakeCommandHandler()


@pytest.fixture
def async_command_handler(command):
    from fractal.core.command_bus.command import Command
    from fractal.core.command_bus.command_handler import CommandHandler

    class FakeCommandHandler(CommandHandler):
        def __init__(self):
            self.command = type(command)

        async def handle(self, command: Command):
            return 1

    return FakeCommandHandler()
