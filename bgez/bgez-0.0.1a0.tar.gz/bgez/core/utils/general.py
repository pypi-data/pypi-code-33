__all__ = [
    'MetaNoInit', 'NoInit', 'Singleton',
]

class MetaNoInit(type):
    __call__ = lambda cls, *args, **kargs: \
        cls.__new__(cls, *args, **kargs)
class NoInit(metaclass=MetaNoInit):
    '''You must call yourself __init__ on the instance'''
class Singleton(NoInit):
    __instance__ = staticmethod(lambda *args, **kargs: None)

    def __new__(cls, *args, **kargs):
        new = cls.__instance__(*args, **kargs)
        if new is not None:
            return new

        new = super().__new__(cls)
        new.__init__(*args, **kargs)
        return new
