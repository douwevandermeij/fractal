import os

from fractal.core.utils.settings import Settings as BaseSettings


class Settings(BaseSettings):
    BASE_DIR = os.path.dirname(__file__)
    ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
    APP_NAME = os.getenv("APP_NAME", "product_system")

    def load(self):
        self.PRODUCT_REPOSITORY_BACKEND = os.getenv("PRODUCT_REPOSITORY_BACKEND", "")
