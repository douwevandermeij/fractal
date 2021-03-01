from enum import Enum


class EnumModel(str, Enum):
    @staticmethod
    def values_dict():
        return {str(r).lower().replace("_", "."): r for r in EnumModel}

    @staticmethod
    def from_string(s):
        return EnumModel.values_dict().get(s)
