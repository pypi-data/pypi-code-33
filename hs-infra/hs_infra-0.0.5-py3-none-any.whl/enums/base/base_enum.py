from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def get_type_by_value(cls, value, default=None) -> 'BaseEnum':
        for type_item in cls:
            if type_item.value == value:
                return type_item
        return default

    @classmethod
    def get_type_by_name(cls, name, default=None) -> 'BaseEnum':
        for type_item in cls:
            if type_item.name == name:
                return type_item
        return default

    @classmethod
    def get_name_by_value(cls, value, default=None) -> str:
        for type_item in cls:
            if type_item.value == value:
                return type_item.name
        return default

    @classmethod
    def get_value_by_name(cls, name: str, default=None):
        for type_item in cls:
            if type_item.name == name:
                return type_item.value
        return default

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
