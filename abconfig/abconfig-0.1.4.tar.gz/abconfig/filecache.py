class Singleton(type):
    _instances = {}

    def __call__(cls, filepath):
        if not filepath in cls._instances:
            cls._instances[filepath] = super(Singleton, cls).__call__(filepath)

        return cls._instances[filepath]


class FileCache(metaclass=Singleton):
    def __init__(self, filepath):
        self.filepath = filepath
        self._data = None

    def get(self):
        return self._data

    def set(self, data):
        self._data = data
