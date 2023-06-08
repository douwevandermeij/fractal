from typing import Generator, Generic, Optional

from fractal_repositories.core.entity import Entity
from fractal_repositories.core.repositories import EntityType, Repository
from fractal_specifications.generic.specification import Specification

from fractal.core.event_sourcing.event_store import EventStore
from fractal.core.event_sourcing.event_stream import EventStream
from fractal.core.event_sourcing.models import EventSourcedAggregateRoot
from fractal.core.exceptions import AggregateRootError


class EventSourcedRepository(Generic[EntityType], Repository[Entity]):
    entity: EntityType = Entity

    def __init__(self, event_store: EventStore, *args, **kwargs):
        self.event_store = event_store
        super().__init__(*args, **kwargs)

    def commit(self, event_stream: EventStream):
        self.event_store.commit(
            event_stream=event_stream,
            aggregate=self.entity.__name__,
            version=1,
        )

    def add(self, entity: Entity) -> Entity:
        if not issubclass(type(entity), EventSourcedAggregateRoot):
            raise AggregateRootError
        self.commit(
            EventStream(
                events=entity.release(),
            )
        )
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        return self.add(entity)

    def remove_one(self, specification: Specification):
        raise NotImplementedError

    def find_one(self, specification: Specification) -> Optional[Entity]:
        raise NotImplementedError

    def find(*args, **kwargs) -> Generator[Entity, None, None]:
        raise NotImplementedError

    def is_healthy(self) -> bool:
        return self.event_store.is_healthy()
