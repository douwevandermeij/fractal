from typing import Optional

from fractal import Fractal
from fractal.core.utils.application_context import ApplicationContext
from fractal.core.utils.settings import Settings


class ApplicationFractal(Fractal):
    def __init__(self, context: ApplicationContext, settings: Optional[Settings]):
        self.context = context
        self.settings = settings
        super(ApplicationFractal, self).__init__()
