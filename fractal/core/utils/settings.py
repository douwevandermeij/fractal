import os
from io import StringIO

from dotenv import load_dotenv


class Settings(object):
    instance = None

    def __new__(cls, dotenv=True, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls, *args, **kwargs)
            if dotenv:
                dotenv_path = None
                if root_dir := getattr(cls, "ROOT_DIR", None):
                    dotenv_path = os.path.join(root_dir, ".env")
                load_dotenv(dotenv_path)
            cls.instance.load()
        return cls.instance

    def load(self):
        pass

    def reload(self, defaults: dict):
        filelike = StringIO("\n".join([f"{k}={v}" for k, v, in defaults.items()]))
        filelike.seek(0)
        load_dotenv(stream=filelike, override=True)
        self.load()
        Settings.instance = self
