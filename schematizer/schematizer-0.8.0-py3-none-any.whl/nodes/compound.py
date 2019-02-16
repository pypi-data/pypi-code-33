from functools import lru_cache

from common.schematizer.exceptions import (
    BaseValidationError, CompoundValidationError, NestedValidationError, SimpleValidationError, StopValidation,
)
from common.schematizer.key import Key
from common.schematizer.nodes.base import Base, BaseCoercible
from dataclasses import make_dataclass


def _force_key(str_or_key):
    if isinstance(str_or_key, Key):
        return str_or_key
    else:
        return Key(str_or_key)


class List(BaseCoercible):
    coerce_primitive = list

    def __init__(self, node):
        super().__init__()
        self.node = node

    def to_native(self, obj):
        obj = super().to_native(obj)
        result = []
        errors = []
        for i, item in enumerate(obj):
            try:
                result.append(self.node.to_native(item))
            except BaseValidationError as exc:
                errors.append(NestedValidationError(i, exc))
        if errors:
            raise CompoundValidationError(errors)
        else:
            return result

    def to_primitive(self, obj):
        return [self.node.to_primitive(item) for item in obj]


class BaseEntity(BaseCoercible):
    coerce_primitive = dict

    def __init__(self, nodes={}):
        super().__init__()
        self.nodes = {
            _force_key(str_or_key): node
            for str_or_key, node in nodes.items()
        }

    def get_native_type(self):
        raise NotImplementedError

    def get_native_accessor(self):
        raise NotImplementedError

    def extended(self, nodes):
        return self.__class__({**self.nodes, **nodes})

    def to_native(self, obj):
        obj = super().to_native(obj)
        result = {}
        errors = []
        for key, node in self.nodes.items():
            try:
                value = obj[key.primitive]
            except KeyError:
                if key.is_required:
                    error = NestedValidationError(
                        key.primitive, SimpleValidationError('MISSING'),
                    )
                    errors.append(error)
                continue
            try:
                result[key.native] = node.to_native(value)
            except BaseValidationError as exc:
                errors.append(
                    NestedValidationError(key.primitive, exc),
                )
        if errors:
            raise CompoundValidationError(errors)
        else:
            native_type = self.get_native_type()
            return native_type(**result)

    def to_primitive(self, obj):
        result = {}
        native_accessor = self.get_native_accessor()
        for key, node in self.nodes.items():
            value = native_accessor(obj, key.native)
            result[key.primitive] = node.to_primitive(value)
        return result


class Dict(BaseEntity):
    def get_native_type(self):
        return dict

    def get_native_accessor(self):
        return dict.__getitem__


class DataClass(BaseEntity):
    @lru_cache(maxsize=None)
    def get_native_type(self):
        return make_dataclass('NativeType', [key.native for key in self.nodes], frozen=True)

    def get_native_accessor(self):
        return getattr


class Called(Base):
    def __init__(self, node, *args, **kwargs):
        self.node = node
        self.args = args
        self.kwargs = kwargs

    def to_native(self, obj):
        return self.node.to_native(obj)

    def to_primitive(self, obj):
        return self.node.to_primitive(
            obj(*self.args, **self.kwargs),
        )


class Wrapped(Base):
    def __init__(self, node, validators):
        super().__init__()
        self.node = node
        self.validators = validators

    def to_native(self, obj):
        try:
            for validator in self.validators:
                validator.validate_primitive(obj)
        except StopValidation:
            return obj
        obj = self.node.to_native(obj)
        for validator in self.validators:
            validator.validate_native(obj)
        return obj

    def to_primitive(self, obj):
        try:
            for validator in self.validators:
                validator.validate_native(obj)
        except StopValidation:
            return obj
        obj = self.node.to_primitive(obj)
        for validator in self.validators:
            validator.validate_primitive(obj)
        return obj
