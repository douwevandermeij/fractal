from dataclasses import dataclass
from typing import Any

from fractal.core.command_bus.command import Command


@dataclass
class Event(object):
    pass


@dataclass
class SendingEvent(Event):
    command: Command

    @property
    def object_id(self):
        raise NotImplementedError

    @staticmethod
    def to_event(event: Any):
        return event


@dataclass
class ReceivingEvent(Event):
    def to_command(self):
        raise NotImplementedError
