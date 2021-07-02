from pydantic import BaseModel

from fractal.core.utils.json_encoder import EnhancedEncoder


class BaseModelEnhancedEncoder(EnhancedEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.dict()
        return super(BaseModelEnhancedEncoder, self).default(o)
