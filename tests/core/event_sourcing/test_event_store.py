import pytest

event_stores = [
    pytest.lazy_fixture("object_event_store"),
    pytest.lazy_fixture("dict_event_store"),
    pytest.lazy_fixture("json_event_store"),
]


def test_event_store_repository_is_healthy(inmemory_event_store_repository):
    assert inmemory_event_store_repository.is_healthy()


@pytest.mark.parametrize("event_store", event_stores)
def test_event_store_is_healthy(event_store):
    assert event_store.is_healthy()


@pytest.mark.parametrize("event_store", event_stores)
def test_event_store_commit(event_store, event_stream):
    event_store.commit(event_stream, "test", 1)

    assert len(event_store.event_store_repository.entities) == len(event_stream.events)
    assert (
        list(event_store.event_store_repository.entities.values())[0].object_id
        == event_stream.events[0].object_id
    )


@pytest.mark.parametrize("event_store", event_stores)
def test_event_store_get_event_stream(event_store, event_stream):
    event_store.commit(event_stream, "test", 1)

    assert len(event_store.get_event_stream().events) == len(event_stream.events)
    assert (
        event_store.get_event_stream().events[0].object_id
        == event_stream.events[0].object_id
    )


@pytest.mark.parametrize(
    "event_store",
    [
        pytest.lazy_fixture("dict_event_store"),
        pytest.lazy_fixture("json_event_store"),
    ],
)
def test_event_store_get_event_stream_error(event_store, not_mapped_event_stream):
    event_store.commit(not_mapped_event_stream, "test", 1)

    from fractal.core.event_sourcing.event_store import EventNotMappedError

    with pytest.raises(EventNotMappedError):
        event_store.get_event_stream()
