from typing import Callable, List, Optional, Union

from fractal.core.command_bus.command_bus import CommandBus
from fractal.core.event_sourcing.event import (
    EventCommandMapper,
    EventProcessMapper,
    ReceivingEvent,
    SendingEvent,
)
from fractal.core.event_sourcing.event_projector import EventProjector


class CommandBusProjector(EventProjector):
    def __init__(
        self,
        command_bus_func: Callable[[], CommandBus],
        command_mappers: List[EventCommandMapper],
        process_mappers: Optional[List[EventProcessMapper]] = None,
    ):
        self.command_bus_func = command_bus_func
        self.command_mappers = {
            event: mapper
            for m in command_mappers
            for event, mapper in m().mappers().items()
        }
        self.process_mappers = {
            event: mapper
            for m in (process_mappers or [])
            for event, mapper in m().mappers().items()
        }

    def project(self, id: str, event: Union[SendingEvent, ReceivingEvent]):
        if isinstance(event, ReceivingEvent):
            self.command_bus_func().handle(event.to_command())

        # Execute command mappers
        elif event.__class__ in self.command_mappers:
            for mapper in self.command_mappers[event.__class__]:
                commands = mapper(event)
                for command in (
                    commands if type(commands) is list else [commands]
                ):  # backwards compatibility
                    if command is not None:  # Skip None returns
                        self.command_bus_func().handle(command)

        # Execute process mappers
        elif event.__class__ in self.process_mappers:
            from fractal.core.process.process import Process
            from fractal.core.process.process_context import ProcessContext

            for mapper in self.process_mappers[event.__class__]:
                process = mapper(event)
                if isinstance(process, Process):
                    # Get ApplicationContext from command bus
                    # Access through closure or command_bus_func
                    from fractal.core.utils.application_context import (
                        ApplicationContext,
                    )

                    # Initialize context with fractal context
                    ctx = ProcessContext(
                        {
                            "fractal": {"context": ApplicationContext()},
                        }
                    )
                    process.run(ctx)
