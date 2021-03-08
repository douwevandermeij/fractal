import datetime
import json
from decimal import Decimal
from uuid import UUID


class EnhancedEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            return o.isoformat()
        elif isinstance(o, set):
            return list(o)
        elif isinstance(o, UUID):
            return str(o)
        elif isinstance(o, Decimal):
            return str(o)
        elif isinstance(o, object):
            return o.__dict__
        return super(EnhancedEncoder, self).default(o)
