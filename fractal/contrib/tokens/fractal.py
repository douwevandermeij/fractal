from typing import Optional

from fractal import Fractal
from fractal.core.utils.application_context import ApplicationContext
from fractal.core.utils.settings import Settings


class DummyTokenServiceFractal(Fractal):
    def __init__(self, context: ApplicationContext, settings: Optional[Settings]):
        self.context = context
        self.token_service = getattr(context, "token_service")
        self.settings = settings
        super(DummyTokenServiceFractal, self).__init__()
