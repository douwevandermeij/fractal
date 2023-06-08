from fractal_repositories.contrib.gcp.firestore.mixins import FirestoreRepositoryMixin

from fractal.core.event_sourcing.event_store import EventStoreRepository
from fractal.core.event_sourcing.message import Message


class FirestoreEventStoreRepository(
    EventStoreRepository, FirestoreRepositoryMixin[Message]
):
    pass
