import functools

__all__ = [
    'Singleton'
]

class MetaSingleton(type):

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        cls.instance = None

    def __call__(cls, *args, **kargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kargs)
        return cls.instance

class Singleton(metaclass=MetaSingleton):
    ...
