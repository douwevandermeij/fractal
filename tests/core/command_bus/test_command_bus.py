import pytest


def test_add_handler(command_bus, command, command_handler):
    command_bus.add_handler(command_handler)

    assert command_bus.handlers[command.__class__.__name__] == [command_handler]


def test_set_handler(command_bus, command, command_handler):
    command_bus.set_handlers([command_handler])

    assert command_bus.handlers[command.__class__.__name__] == [command_handler]


def test_handle(command_bus, command, command_handler):
    command_bus.add_handler(command_handler)

    assert command_bus.handle(command)[command_handler.__class__.__name__] == 1


@pytest.mark.asyncio
async def test_handle_async(command_bus, command, async_command_handler):
    command_bus.add_handler(async_command_handler)

    assert (await command_bus.handle_async(command))[
        async_command_handler.__class__.__name__
    ] == 1
