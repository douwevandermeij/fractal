def test_print_event_projector(print_event_projector, sending_event, capsys):
    import uuid

    id = str(uuid.uuid4())
    print_event_projector.project(id, sending_event)

    printed = capsys.readouterr().out
    assert sending_event.__class__.__name__ in printed
    assert id in printed
