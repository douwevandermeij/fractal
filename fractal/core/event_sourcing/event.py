from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Type

from fractal.core.command_bus.command import Command


@dataclass
class Event(object):
    pass


@dataclass
class BasicSendingEvent(Event, ABC):
    @property
    @abstractmethod
    def object_id(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def aggregate_root_id(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def aggregate_root_type(self):
        raise NotImplementedError


@dataclass
class SendingEvent(BasicSendingEvent, ABC):
    command: Command

    @staticmethod
    def to_event(event: Any):
        return event


@dataclass
class ReceivingEvent(Event):
    def to_command(self):
        raise NotImplementedError


class EventCommandMapper(ABC):
    @abstractmethod
    def mappers(self) -> Dict[Type[Event], List[Callable[[Event], Command]]]:
        raise NotImplementedError
