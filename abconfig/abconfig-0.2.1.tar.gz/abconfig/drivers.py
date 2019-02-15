import yaml

try:
    import ujson as json
except ImportError:
    import json

from os import path
from abc import ABC

from .filecache import FileCache


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
