from io import StringIO

from dotenv import load_dotenv


class Settings(object):
    instance = None

    def __new__(cls, dotenv=True, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls, *args, **kwargs)
            if dotenv:
                load_dotenv()
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
