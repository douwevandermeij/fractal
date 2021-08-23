import pytest


def test_commit(event_sourced_repository, event_stream):
    event_sourced_repository.commit(event_stream)

    assert len(
        event_sourced_repository.event_store.event_store_repository.entities
    ) == len(event_stream.events)
    assert (
        list(
            event_sourced_repository.event_store.event_store_repository.entities.values()
        )[0].object_id
        == event_stream.events[0].object_id
    )


def test_add(event_sourced_repository, aggregate_root_object_with_recorded_event):
    event_sourced_repository.add(aggregate_root_object_with_recorded_event)

    assert (
        len(event_sourced_repository.event_store.event_store_repository.entities) == 1
    )


def test_add_error(event_sourced_repository, regular_object):
    from fractal.core.exceptions import AggregateRootError

    with pytest.raises(AggregateRootError):
        event_sourced_repository.add(regular_object)


def test_update(event_sourced_repository, aggregate_root_object_with_recorded_event):
    event_sourced_repository.update(aggregate_root_object_with_recorded_event)

    assert (
        len(event_sourced_repository.event_store.event_store_repository.entities) == 1
    )


def test_update_error(event_sourced_repository, regular_object):
    from fractal.core.exceptions import AggregateRootError

    with pytest.raises(AggregateRootError):
        event_sourced_repository.update(regular_object)


def test_is_healthy(event_sourced_repository):
    assert event_sourced_repository.is_healthy()
