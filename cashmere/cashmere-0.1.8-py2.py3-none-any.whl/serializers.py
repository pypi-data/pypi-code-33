import collections
import json
import functools
import inspect
import types
import warnings
import enum
import pathlib
import hashlib

import attr
import multipledispatch

from . import core


class NotSerializableWarning(Warning):
    pass


class ErrorAction(enum.Enum):
    RAISE = enum.auto()
    WARN = enum.auto()
    IGNORE = enum.auto()


@attr.s
class Serializable:
    name = attr.ib()
    type = attr.ib()
    value = attr.ib(default=core.UNKNOWN)
    module = attr.ib(default=None)


to_json_serializable = multipledispatch.Dispatcher("registry")


@to_json_serializable.register(object)
def _(obj):
    try:
        return attr.asdict(obj)
    except attr.exceptions.NotAnAttrsClassError:
        return obj


@to_json_serializable.register(core.InputCollection)
def _(obj):
    return collections.OrderedDict(
        [(k, to_json_serializable(v)) for k, v in attr.asdict(obj).items()]
    )


@to_json_serializable.register(types.ModuleType)
def _(obj):
    try:
        string = inspect.getsource(obj)
        type_name = "PythonModule"
    except TypeError:
        string = obj.__name__
        type_name = "BuiltinModule"

    return Serializable(obj.__name__, type_name, string)


@to_json_serializable.register(type)
def _(obj):
    try:
        string = inspect.getsource(obj)
        type_name = "PythonType"
    except TypeError:
        string = obj.__name__
        type_name = "BuiltinType"

    return Serializable(obj.__name__, type_name, string)


@to_json_serializable.register(types.BuiltinFunctionType)
def _(obj):
    return Serializable(
        obj.__name__, type(obj).__name__, value=core.NO_VALUE, module=obj.__module__
    )


@to_json_serializable.register((types.FunctionType))
def _(obj):
    recursed = {
        name: to_json_serializable(value)
        for name, value in core.get_closure(obj).items()
    }
    value = {"source": inspect.getsource(obj), "recursed": recursed}
    return Serializable(obj.__name__, type(obj).__name__, value, module=obj.__module__)


@to_json_serializable.register(inspect.BoundArguments)
def _(obj):
    obj.apply_defaults()
    return Serializable("signature", type(obj).__name__, obj.arguments)


@to_json_serializable.register(pathlib.Path)
def _(obj):
    return repr(obj)


@attr.s
class JSONSerializer:
    dispatcher = attr.ib(factory=lambda: multipledispatch.Dispatcher("registry"))
    on_error = attr.ib(default=ErrorAction.RAISE)

    def dispatch(self, type):
        def wrap(function):
            self.dispatcher.register(type)
            return function

        return wrap

    def __call__(self, obj):
        raw_key = json.dumps(obj, default=self._dumps, sort_keys=True)
        hashed_key = hashlib.sha1(raw_key.encode("utf8")).hexdigest()
        return hashed_key

    def _dumps(self, obj):
        try:
            return self.dispatcher(obj)
        except NotImplementedError:
            if self.on_error == ErrorAction.RAISE:
                raise NotImplementedError(obj)
            if self.on_error == ErrorAction.WARN:
                warnings.warn(f"Not serializable: {obj}", NotSerializableWarning)
                return repr(obj)
            if self.on_error == ErrorAction.IGNORE:
                return repr(obj)
            raise

    def copy(self):
        dispatcher = type(self.dispatcher)(
            name=self.dispatcher.name + "_copy", doc=self.dispatcher.doc
        )
        dispatcher.funcs = self.dispatcher.funcs.copy()
        return attr.evolve(self, dispatcher=dispatcher)

    def register(self, *args, **kwargs):
        return self.dispatcher.register(*args, **kwargs)


json_serializer = JSONSerializer(dispatcher=to_json_serializable)
