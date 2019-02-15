import yaml

try:
    import ujson as json
except ImportError:
    import json

from os import path
from abc import ABC


class FileStore(type):
    _instances = {}

    def __call__(cls, filepath):
        if not filepath in cls._instances:
            cls._instances[filepath] = super(FileStore, cls).__call__(filepath)

        return cls._instances[filepath]


class FileCache(metaclass=FileStore):
    def __init__(self, filepath):
        self.filepath = filepath
        self._data = None

    def get(self):
        return self._data

    def set(self, data):
        self._data = data


class FileDriver(ABC):
    def __init__(self, filepath: str):
        self.filepath = filepath
        filename, extension = path.splitext(self.filepath)
        if not extension:
            if path.exists(filename) is False:
                self.filepath += '.' + type(self).__name__.lower()

    def handle(self):
        raise NotImplementedError

    @classmethod
    def read(cls, filepath: str) -> dict:
        cache = FileCache(filepath)
        if cache.get():
            return cache.get()

        obj = cls(filepath)
        cache.set(obj.handle())
        return cache.get()


class Yaml(FileDriver):
    def handle(self) -> dict:
        with open(self.filepath, 'r') as f:
            return yaml.load(f)


class Json(FileDriver):
    def handle(self) -> dict:
        with open(self.filepath, 'r') as f:
            return json.load(f)
