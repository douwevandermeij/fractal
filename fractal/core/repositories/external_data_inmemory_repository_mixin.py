from dataclasses import asdict
from typing import Dict, List, Tuple, Type

from fractal.core.repositories import Entity
from fractal.core.repositories.inmemory_repository_mixin import InMemoryRepositoryMixin


class ExternalDataInMemoryRepositoryMixin(InMemoryRepositoryMixin[Entity]):
    def __init__(self, klass: Type[Entity]):
        super(ExternalDataInMemoryRepositoryMixin, self).__init__()
        self.klass = klass

    def load_data(self, data: Dict):
        key = self.klass.__name__.lower()
        self.entities = {e["id"]: self.klass(**e) for e in data.get(key, [])}

    def dump_data(self) -> Tuple[str, List[Dict]]:
        return self.klass.__name__.lower(), [asdict(e) for e in self.entities.values()]
