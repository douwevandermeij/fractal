from app.context import ApplicationContext
from app.settings import Settings

from fractal import Fractal


class ApplicationFractal(Fractal):
    settings = Settings()
    context = ApplicationContext()
