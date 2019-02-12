import functools
import json
import tempfile
import hashlib
import pathlib
import warnings

warnings.filterwarnings(
    "ignore", message="Using or importing the ABCs", category=DeprecationWarning
)

import attr
import dataset
import sqlalchemy.exc
import sqlite3

from . import core
from . import serializers
from . import autoserial
from . import utils


class NoCache(Exception):
    pass


@attr.s
class MemoryCache:

    key_serializer = attr.ib(default=serializers.json_serializer)
    value_serializer = attr.ib(default=None)
    _data = attr.ib(factory=dict)

    def memoize(self, function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            call = core.FunctionCall.from_args(function, args, kwargs)
            key = json.dumps(call, default=self.key_serializer, sort_keys=True)

            if key in self._data:
                return self._data[key]

            result = function(*args, **kwargs)
            self._data[key] = result
            return result

        return wrapper


@attr.s
class DirectoryCache:

    key_serializer = attr.ib(serializers.json_serializer)
    value_serializer = attr.ib(default=autoserial.auto_serialize)
    value_deserializer = attr.ib(default=autoserial.auto_deserialize)
    directory = attr.ib(
        factory=lambda: pathlib.Path(tempfile.TemporaryDirectory().name)
    )
    codec = attr.ib(factory=autoserial.AutoCodec)

    # @utils.reify
    @property
    def index(self):
        try:
            return dataset.connect(
                "sqlite:///" + str((self.directory / "index.sqlite").resolve())
            )["file"]
        except (sqlalchemy.exc.OperationalError, sqlite3.OperationalError):
            raise FileNotFoundError

    def memoize(self, function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            call = core.FunctionCall.from_args(function, args, kwargs)
            hashed_key = self.key_serializer(call)
            path = pathlib.Path(self.directory) / hashed_key
            try:
                result = self._deserialize_value(path)
            except NoCache:
                result = function(*args, **kwargs)
                self._serialize_value(result, path)
            return result

        return wrapper

    def _deserialize_value(self, path):
        if not path.exists():
            raise NoCache

        row = self.index.find_one(hash=path.name)
        if row is None:
            raise NoCache
        codec_name = row["codec_name"]

        codec = self.codec._registry[codec_name]

        with open(path, "rb" if codec.binary else "rt") as f:
            return codec.load(f)

    def _serialize_value(self, result, path):
        codec = self.codec._registry[type(result).__name__]

        path.parent.mkdir(exist_ok=True)
        self.index.insert(dict(hash=path.name, codec_name=type(result).__name__))
        with open(path, "wb" if codec.binary else "wt") as f:
            codec.dump(result, f)


@attr.s
class NullCache:
    def memoize(self, function):
        return function
