import datetime
import json
from dataclasses import asdict

from fractal.core.event_sourcing.event import SendingEvent
from fractal.core.event_sourcing.event_projector import EventProjector
from fractal.core.event_sourcing.message import Message
from fractal.core.utils.json_encoder import EnhancedEncoder


class PrintEventProjector(EventProjector):
    def project(self, id: str, event: SendingEvent):
        message = Message(
            id=id,
            occurred_on=datetime.datetime.now(tz=datetime.timezone.utc),
            event=event.__class__.__name__,
            data=event,
            object_id=str(event.object_id),
            aggregate_root_id=str(event.aggregate_root_id),
        )
        print(json.dumps(asdict(message), cls=EnhancedEncoder))
