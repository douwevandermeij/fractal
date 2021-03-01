import dataclasses
from dataclasses import dataclass
from enum import Enum


@dataclass
class Model:
    @classmethod
    def clean(cls, **kwargs):
        field_names = set(f.name for f in dataclasses.fields(cls))
        return cls(**{k: v for k, v in kwargs.items() if k in field_names})

    @classmethod
    def from_dict(cls, data):
        return cls.clean(**data)


class EnumModel(str, Enum):
    @staticmethod
    def values_dict():
        return {str(r).lower().replace("_", "."): r for r in EnumModel}

    @staticmethod
    def from_string(s):
        return EnumModel.values_dict().get(s)
