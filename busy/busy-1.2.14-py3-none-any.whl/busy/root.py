# A queue manager, which happens to use the file system

from pathlib import Path
from tempfile import TemporaryDirectory
import os

from .file import File
from .queue import Queue


class Root:

    def __init__(self, path=None):
        if path:
            self.path = path
        self._files = {}
        self._queues = {}

    @property
    def path(self):
        if not hasattr(self, '_path'):
            env_var = os.environ.get('BUSY_ROOT')
            self._path = Path(env_var if env_var else Path.home() / '.busy')
            if not self._path.is_dir():
                self._path.mkdir()
        return self._path

    @path.setter
    def path(self, value):
        assert not hasattr(self, '_path')
        path = Path(value) if isinstance(value, str) else value
        assert isinstance(path, Path) and path.is_dir()
        self._path = path

    def get_queue(self, key=None):
        key = key or Queue.default_key
        if key not in self._queues:
            queueclass = Queue.subclass(key)
            queuefile = File(self.path / f'{key}.txt')
            self._files[key] = queuefile
            self._queues[key] = queueclass(self)
            self._queues[key].add(*queuefile.read(queueclass.itemclass))
        return self._queues[key]

    def save(self):
        while self._queues:
            key, queue = self._queues.popitem()
            items = queue.all()
            self._files[key].save(*items)
