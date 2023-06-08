from dataclasses import dataclass

import pytest


@pytest.fixture
def print_event_projector():
    from fractal.core.event_sourcing.projectors.print_projector import (
        PrintEventProjector,
    )

    return PrintEventProjector()


@pytest.fixture
def sending_event(command):
    from fractal.core.event_sourcing.event import SendingEvent

    @dataclass
    class FakeSendingEvent(SendingEvent):
        id: str

        @property
        def object_id(self):
            return self.id

        @property
        def aggregate_root_id(self):
            return self.id

        @property
        def aggregate_root_type(self):
            return self.__class__

    return FakeSendingEvent(command, "1")


@pytest.fixture
def not_mapped_sending_event(command):
    from fractal.core.event_sourcing.event import SendingEvent

    @dataclass
    class NotMappedSendingEvent(SendingEvent):
        id: str

        @property
        def object_id(self):
            return self.id

        @property
        def aggregate_root_id(self):
            return self.id

        @property
        def aggregate_root_type(self):
            return self.__class__

    return NotMappedSendingEvent(command, "1")


@pytest.fixture
def event_publisher(print_event_projector):
    from fractal.core.event_sourcing.event_publisher import EventPublisher

    return EventPublisher([print_event_projector])


@pytest.fixture
def inmemory_event_store_repository():
    from fractal_repositories.mixins.inmemory_repository_mixin import (
        InMemoryRepositoryMixin,
    )

    from fractal.core.event_sourcing.event_store import EventStoreRepository
    from fractal.core.event_sourcing.message import Message

    class InMemoryEventStoreRepository(
        EventStoreRepository, InMemoryRepositoryMixin[Message]
    ):
        pass

    return InMemoryEventStoreRepository()


@pytest.fixture
def object_event_store(inmemory_event_store_repository):
    from fractal.core.event_sourcing.event_store import ObjectEventStore

    return ObjectEventStore(inmemory_event_store_repository)


@pytest.fixture
def dict_event_store(inmemory_event_store_repository, sending_event):
    from fractal.core.event_sourcing.event_store import DictEventStore

    return DictEventStore(inmemory_event_store_repository, [sending_event.__class__])


@pytest.fixture
def json_event_store(inmemory_event_store_repository, sending_event):
    from fractal.core.event_sourcing.event_store import JsonEventStore

    return JsonEventStore(inmemory_event_store_repository, [sending_event.__class__])


@pytest.fixture
def event_stream(sending_event):
    from fractal.core.event_sourcing.event_stream import EventStream

    return EventStream(events=[sending_event])


@pytest.fixture
def not_mapped_event_stream(not_mapped_sending_event):
    from fractal.core.event_sourcing.event_stream import EventStream

    return EventStream(events=[not_mapped_sending_event])


@pytest.fixture
def event_sourced_repository(json_event_store, aggregate_root_object):
    from fractal.core.event_sourcing.repositories import EventSourcedRepository

    class FakeEventSourcedRepository(
        EventSourcedRepository[aggregate_root_object.__class__]
    ):
        entity = aggregate_root_object.__class__

    return FakeEventSourcedRepository(json_event_store)


@pytest.fixture
def aggregate_root_object():
    from fractal.core.event_sourcing.models import EventSourcedAggregateRoot

    @dataclass
    class AggregateRoot(EventSourcedAggregateRoot):
        id: str
        name: str = "default_name"

    return AggregateRoot("1")


@pytest.fixture
def aggregate_root_object_with_recorded_event(aggregate_root_object, sending_event):
    aggregate_root_object.record(sending_event)

    return aggregate_root_object


@pytest.fixture
def regular_object():
    @dataclass
    class Regular:
        id: str
        name: str = "default_name"

    return Regular("1")
