# http://code.activestate.com/recipes/496741-object-proxying/

TARGET = '_object'
MAGIC_METHODS = [
    '__await__', '__aiter__', '__anext__', '__aenter__', '__aexit__',
    '__get__', '__set__', '__delete__', '__set_name__',

    '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
    '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
    '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
    '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
    '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
    '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
    '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
    '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
    '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
    '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
    '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
    '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
    '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
    '__truediv__', '__xor__', 'next',
]

__all__ = [
    'Proxy',
]

class Proxy:
    __slots__ = [TARGET, '__weakref__']

    def __getattribute__(self, name: str) -> object:
        try: return getattr(object.__getattribute__(self, TARGET), name)
        except AttributeError as target_error:
            try: return object.__getattribute__(self, name)
            except AttributeError as self_error:
                raise AttributeError(f'\n {target_error}\n {self_error}')
    def __setattr__(self, name: str, value: object):
        setattr(object.__getattribute__(self, TARGET), name, value)
    def __delattr__(self, name: str):
        delattr(object.__getattribute__(self, TARGET), name)

    __nonzero__ = lambda self: bool(object.__getattribute__(self, TARGET))
    __str__ = lambda self: str(object.__getattribute__(self, TARGET))
    __repr__ = lambda self: repr(object.__getattribute__(self, TARGET))

    @classmethod
    def __create_class_proxy(cls, klass: type) -> type:
        method = lambda name: \
            lambda self, *args, **kargs: \
                getattr(object.__getattribute__(self, TARGET), name)(*args, **kargs)

        namespace = dict(__ORIGIN__ = klass)
        for name in MAGIC_METHODS:
            if hasattr(klass, name):
                namespace[name] = method(name)

        return type(f'{cls.__name__}({klass.__name__})', (cls,), namespace)

    def __new__(cls, target: object, *args, **kargs) -> object:
        try:
            cache = cls.__dict__['_class_proxy_cache']
        except KeyError:
            cache = cls._class_proxy_cache = {}
        try:
            klass = cache[target.__class__]
        except KeyError:
            klass = cache[target.__class__] = \
                cls.__create_class_proxy(target.__class__)

        instance = object.__new__(klass)
        return instance

    def __set_target(self, target: object):
        cls = object.__getattribute__(self, '__class__')
        if target.__class__ is not cls.__ORIGIN__:
            raise TypeError(f'object {target} is not compatible with {self.__class__}')
        object.__setattr__(self, TARGET, target)
        return self

    def __init__(self, target: object):
        self.__set_target(target)
