def test_publish_event(event_publisher, sending_event, capsys):
    event_publisher.publish_event(sending_event)

    assert sending_event.__class__.__name__ in capsys.readouterr().out


def test_publish_events(event_publisher, sending_event, capsys):
    event_publisher.publish_events([sending_event])

    assert sending_event.__class__.__name__ in capsys.readouterr().out
