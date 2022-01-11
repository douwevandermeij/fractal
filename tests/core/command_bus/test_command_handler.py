def test_command_handler_commands(command, command_handler):
    assert command_handler.command == type(command)
