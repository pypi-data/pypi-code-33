from .._plum import Plum
from ._tupleclass import TupleClass


class Tuple(tuple, Plum, metaclass=TupleClass):

    _types = ()
    _nbytes = 0

    def __new__(cls, iterable=tuple()):
        item_values = tuple(iterable)
        types = cls._types
        assert len(item_values) == len(types)
        items = (arg if type(arg) is typ else typ(arg) for arg, typ in zip(iterable, types))
        return tuple.__new__(cls, items)

    @classmethod
    def __unpack__(cls, memory, dump):
        if dump:
            dump.cls = cls

            self = tuple.__new__(
                cls, (typ.__unpack__(
                    memory,
                    dump.add_level(access=f'[{i}]'))
                    for i, typ in enumerate(cls._types)))
        else:
            self = tuple.__new__(cls, (typ.__unpack__(memory, dump) for typ in cls._types))

        return self

    @classmethod
    def __pack__(cls, items, dump):
        if not isinstance(items, cls):
            items = cls(items)

        if dump:
            dump.cls = cls

            for i, item in enumerate(items):
                yield from item.__pack__(item, dump.add_level(access=f'[{i}]'))
        else:
            for i, item in enumerate(items):
                yield from item.__pack__(item, dump)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self)
