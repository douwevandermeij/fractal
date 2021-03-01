import datetime
import json
from dataclasses import asdict
from typing import Type

from fractal.core.event_sourcing import EventProjector, Message, SendingEvent
from fractal.core.utils import EnhancedEncoder


class PrintEventProjector(EventProjector):
    def project(self, id: str, event: Type[SendingEvent]):
        message = Message(
            id=id,
            occurred_on=datetime.datetime.now(tz=datetime.timezone.utc),
            event_type=event.__class__.__name__,
            event=event,
            object_id=str(event.object_id),
        )
        print(json.dumps(asdict(message), cls=EnhancedEncoder))
