import json
from dataclasses import asdict
from typing import Dict, List, Tuple, Type

from fractal.core.repositories import Entity
from fractal.core.repositories.inmemory_repository_mixin import InMemoryRepositoryMixin
from fractal.core.utils.json_encoder import EnhancedEncoder


class ExternalDataInMemoryRepositoryMixin(InMemoryRepositoryMixin[Entity]):
    def __init__(self, klass: Type[Entity]):
        super(ExternalDataInMemoryRepositoryMixin, self).__init__()
        self.klass = klass

    def load_data_dict(self, data: Dict):
        key = self.klass.__name__.lower()
        self.entities = {e["id"]: self.klass(**e) for e in data.get(key, [])}

    def dump_data_dict(self) -> Tuple[str, List[Dict]]:
        return self.klass.__name__.lower(), [asdict(e) for e in self.entities.values()]

    def load_data_json(self, data: Dict):
        key = self.klass.__name__.lower()
        self.entities = {
            e["id"]: self.klass(**e) for e in json.loads(data.get(key, []))
        }

    def dump_data_json(self) -> Tuple[str, str]:
        _, data = self.dump_data_dict()
        return self.klass.__name__.lower(), json.dumps(data, cls=EnhancedEncoder)
