import json

import attr
import multipledispatch

from . import utils

auto_serialize = utils.ExtensibleDispatcher()
auto_deserialize = utils.ExtensibleDispatcher()


@attr.s
class ValueCodec:
    type = attr.ib()
    name = attr.ib(default=None)
    dump = attr.ib(default=lambda x: x)
    load = attr.ib(default=lambda x: x)
    binary = attr.ib(default=False)


@attr.s
class AutoCodec:
    _registry = attr.ib(factory=dict)

    def serializer(self, type):
        def wrapper(func):
            try:
                value_codec = self._registry[type.__name__]
            except KeyError:
                self._registry[type.__name__] = ValueCodec(
                    type, type.__name__, dump=func
                )
            else:
                self._registry[type.__name__] = attr.evolve(value_codec, dump=func)
            return func

        return wrapper

    def deserializer(self, type):
        def wrapper(func):
            try:
                value_codec = self._registry[type.__name__]
            except KeyError:
                self._registry[type.__name__] = ValueCodec(
                    type, type.__name__, load=func
                )
            else:
                self._registry[type.__name__] = attr.evolve(value_codec, load=func)
            return func

        return wrapper

    def register(self, value_codec):
        self._registry[value_codec.type.__name__] = value_codec
