from abc import ABC


class Service(ABC):
    def is_healthy(self) -> bool:
        return True
