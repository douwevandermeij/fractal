from fractal import Fractal

from app.context import ApplicationContext
from app.settings import Settings


class ApplicationFractal(Fractal):
    settings = Settings()
    context = ApplicationContext()
