import json
import pickle
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from json import JSONEncoder
from typing import List, Optional, Type

from fractal.core.event_sourcing.event import BasicSendingEvent
from fractal.core.event_sourcing.event_stream import EventStream
from fractal.core.event_sourcing.message import Message
from fractal.core.exceptions import DomainException
from fractal.core.repositories import Repository
from fractal.core.specifications.generic.specification import Specification


class EventNotMappedError(DomainException):
    code = "EVENT_NOT_MAPPED_ERROR"
    status_code = 501

    def __init__(self, event: str):
        super(EventNotMappedError, self).__init__(
            f"Event '{event}' is not mapped to be loaded from the EventStore.",
        )


class EventStore(ABC):
    @abstractmethod
    def commit(self, event_stream: EventStream, aggregate: str, version: int):
        raise NotImplementedError

    @abstractmethod
    def get_event_stream(self) -> EventStream:
        raise NotImplementedError

    @abstractmethod
    def is_healthy(self) -> bool:
        raise NotImplementedError


class EventStoreRepository(Repository[Message], ABC):
    entity = Message


class BasicEventStore(EventStore, ABC):
    def __init__(self, event_store_repository: EventStoreRepository):
        self.event_store_repository = event_store_repository

    def is_healthy(self) -> bool:
        return self.event_store_repository.is_healthy()


class ObjectEventStore(BasicEventStore):
    def commit(self, event_stream: EventStream, aggregate: str, version: int):
        for event in event_stream.events:
            self.event_store_repository.add(
                Message(
                    id=str(uuid.uuid4()),
                    occurred_on=datetime.utcnow(),
                    event=event.__class__.__name__,
                    data=event,
                    object_id=event.object_id,
                )
            )

    def get_event_stream(
        self, specification: Optional[Specification] = None
    ) -> EventStream:
        return EventStream(
            events=list(
                map(lambda m: m.data, self.event_store_repository.find(specification))
            )
        )


class DictEventStore(BasicEventStore):
    def __init__(
        self,
        event_store_repository: EventStoreRepository,
        events: List[Type[BasicSendingEvent]],
    ):
        super(DictEventStore, self).__init__(event_store_repository)
        self.events = {e.__name__: e for e in events}

    def commit(self, event_stream: EventStream, aggregate: str, version: int):
        for event in event_stream.events:
            self.event_store_repository.add(
                Message(
                    id=str(uuid.uuid4()),
                    occurred_on=datetime.utcnow(),
                    event=event.__class__.__name__,
                    data=asdict(event),
                    object_id=event.object_id,
                )
            )

    def get_event_stream(
        self, specification: Optional[Specification] = None
    ) -> EventStream:
        events = []
        for m in self.event_store_repository.find(specification):
            if event := self.events.get(m.event, None):
                events.append(event(**m.data))
            else:
                raise EventNotMappedError(m.event)
        return EventStream(events=events)


class JsonEventStore(BasicEventStore):
    def __init__(
        self,
        event_store_repository: EventStoreRepository,
        events: List[Type[BasicSendingEvent]],
        json_encoder: Optional[Type[JSONEncoder]] = None,
    ):
        super(JsonEventStore, self).__init__(event_store_repository)
        self.events = {e.__name__: e for e in events}
        self.json_encoder = json_encoder

    def commit(self, event_stream: EventStream, aggregate: str, version: int):
        for event in event_stream.events:
            self.event_store_repository.add(
                Message(
                    id=str(uuid.uuid4()),
                    occurred_on=datetime.utcnow(),
                    event=event.__class__.__name__,
                    data=json.dumps(asdict(event), cls=self.json_encoder),
                    object_id=event.object_id,
                )
            )

    def get_event_stream(
        self, specification: Optional[Specification] = None
    ) -> EventStream:
        events = []
        for m in self.event_store_repository.find(specification):
            if event := self.events.get(m.event, None):
                events.append(event(**json.loads(m.data)))
            else:
                raise EventNotMappedError(m.event)
        return EventStream(events=events)


class PickleEventStore(BasicEventStore):
    def __init__(
        self,
        event_store_repository: EventStoreRepository,
        events: List[Type[BasicSendingEvent]],
    ):
        super(PickleEventStore, self).__init__(event_store_repository)
        self.events = {e.__name__: e for e in events}

    def commit(self, event_stream: EventStream, aggregate: str, version: int):
        for event in event_stream.events:
            self.event_store_repository.add(
                Message(
                    id=str(uuid.uuid4()),
                    occurred_on=datetime.utcnow(),
                    event=event.__class__.__name__,
                    data=pickle.dumps(event),
                    object_id=event.object_id,
                )
            )

    def get_event_stream(
        self, specification: Optional[Specification] = None
    ) -> EventStream:
        events = []
        for m in self.event_store_repository.find(specification):
            events.append(pickle.loads(m.data))
        return EventStream(events=events)
