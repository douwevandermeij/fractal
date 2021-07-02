from typing import Generator, Generic, Optional

from fractal.core.event_sourcing.event_store import EventStore
from fractal.core.event_sourcing.event_stream import EventStream
from fractal.core.event_sourcing.models import EventSourcedAggregateRoot
from fractal.core.exceptions import AggregateRootError
from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.specification import Specification


class EventSourcedRepository(Generic[Entity], Repository[Entity]):
    entity = Entity

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def commit(self, event_stream: EventStream):
        self.event_store.commit(
            event_stream=event_stream,
            aggregate=self.entity.__name__,
            version=1,
        )

    def add(self, entity: Entity) -> Entity:
        if not isinstance(entity, EventSourcedAggregateRoot):
            raise AggregateRootError
        self.commit(
            EventStream(
                events=entity.release(),
            )
        )
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        if not isinstance(entity, EventSourcedAggregateRoot):
            raise AggregateRootError
        self.commit(
            EventStream(
                events=entity.release(),
            )
        )
        return entity

    def remove_one(self, specification: Specification):
        raise NotImplementedError()

    def find_one(self, specification: Specification) -> Optional[Entity]:
        raise NotImplementedError()

    def find(
        self, specification: Specification = None
    ) -> Generator[Entity, None, None]:
        raise NotImplementedError()

    def is_healthy(self) -> bool:
        return self.event_store.is_healthy()
