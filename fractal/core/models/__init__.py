from dataclasses import asdict, dataclass, fields
from enum import Enum
from typing import Dict


@dataclass
class Model:
    @classmethod
    def clean(cls, **kwargs):
        field_names = set(f.name for f in fields(cls))
        return cls(**{k: v for k, v in kwargs.items() if k in field_names})  # NOQA

    @classmethod
    def from_dict(cls, data):
        return cls.clean(**data)

    def update(self, model: Dict):
        current = asdict(self)
        current.update(model)
        return self.from_dict(current)


@dataclass
class Contract(Model):
    pass


@dataclass
class CleanContract(Contract):
    @classmethod
    def clean(cls, **kwargs):
        if "$type" in kwargs:
            kwargs["type"] = kwargs["$type"]
        return super(CleanContract, cls).clean(**kwargs)


class EnumModel(str, Enum):
    @staticmethod
    def values_dict():
        return {str(r).lower().replace("_", "."): r for r in EnumModel}

    @staticmethod
    def from_string(s):
        return EnumModel.values_dict().get(s)
