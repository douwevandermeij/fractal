from dataclasses import asdict, dataclass, fields
from datetime import date
from decimal import Decimal
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

    def asdict(self, *, skip_types=None):
        if skip_types is None:
            skip_types = []
        field_names = set(
            f.name for f in fields(self) if f.name not in self.calculated_fields()
        )

        def _asdict(v):
            if isinstance(v, Model):
                return v.asdict(skip_types=skip_types)
            elif isinstance(v, list) and list not in skip_types:
                return [_asdict(i) for i in v]
            elif isinstance(v, Decimal) and Decimal not in skip_types:
                return f"{v:.2f}"
            elif isinstance(v, date) and date not in skip_types:
                return v.isoformat()
            return v

        ret = {k: _asdict(v) for k, v in self.__dict__.items() if k in field_names}
        return ret

    @staticmethod
    def calculated_fields():
        return []


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
