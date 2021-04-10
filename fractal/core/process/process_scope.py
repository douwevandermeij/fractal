from typing import Dict, Optional


class ProcessScope:
    def __init__(self, data: Optional[Dict] = None):
        self.data = data or {}

    def __getattr__(self, item):
        return self.data.get(item)

    def __getitem__(self, item):
        return self.data.get(item)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return self.data.__repr__()

    def update(self, scope: "ProcessScope") -> "ProcessScope":
        self.data.update(scope.data)
        return self

    def get(self, key, default=None):
        return self.data.get(key, default)
