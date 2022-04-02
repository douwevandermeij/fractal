from typing import Callable, List, Union

from fractal.core.command_bus.command_bus import CommandBus
from fractal.core.event_sourcing.event import (
    EventCommandMapper,
    ReceivingEvent,
    SendingEvent,
)
from fractal.core.event_sourcing.event_projector import EventProjector


class CommandBusProjector(EventProjector):
    def __init__(
        self,
        command_bus_func: Callable[[], CommandBus],
        mappers: List[EventCommandMapper],
    ):
        self.command_bus_func = command_bus_func
        self.mappers = {
            event: mapper for m in mappers for event, mapper in m().mappers().items()
        }

    def project(self, id: str, event: Union[SendingEvent, ReceivingEvent]):
        if isinstance(event, ReceivingEvent):
            self.command_bus_func().handle(event.to_command())
        elif event.__class__ in self.mappers:
            for mapper in self.mappers[event.__class__]:
                self.command_bus_func().handle(mapper(event))
