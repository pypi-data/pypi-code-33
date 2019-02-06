# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from .._plum import Plum
from ..int.little import UInt8
from ._arrayclass import ArrayClass, GREEDY_DIMS


class Array(list, Plum, metaclass=ArrayClass):

    # filled in by metaclass
    _dims = GREEDY_DIMS
    _item_cls = UInt8
    _nbytes = None

    @classmethod
    def __unpack__(cls, memory, dump, outer_level=True):

        if dump and outer_level:
            dump.cls = cls

        self = list.__new__(cls)
        list.__init__(self)

        item_cls = cls._item_cls

        dims = cls._dims

        if dims == GREEDY_DIMS:
            end = memory.buffer.nbytes
            i = 0
            if dump:
                kwargs = dict(outer_level=False) if issubclass(cls, Array) else {}
                while memory.cursor < end:
                    subdump = dump.add_level(access=f'[{i}]')
                    list.append(self, item_cls.__unpack__(memory, subdump, **kwargs))
                    i += 1
            else:
                while memory.cursor < end:
                    list.append(self, item_cls.__unpack__(memory, None))
                    i += 1
        else:
            if dump:
                kwargs = dict(outer_level=False) if issubclass(cls, Array) else {}
                for i in range(dims[0]):
                    subdump = dump.add_level(access=f'[{i}]')
                    list.append(self, item_cls.__unpack__(memory, subdump, **kwargs))
            else:
                for i in range(dims[0]):
                    list.append(self, item_cls.__unpack__(memory, None))

        return self

    @classmethod
    def __pack__(cls, items, dump, outer_level=True):
        if not isinstance(items, cls):
            items = cls(items)

        if dump:
            if outer_level:
                dump.cls = cls

            kwargs = dict(outer_level=False) if issubclass(cls._item_cls, Array) else {}

            for i, item in enumerate(items):
                yield from item.__pack__(item, dump.add_level(access=f'[{i}]'), **kwargs)
        else:
            for item in items:
                yield from item.__pack__(item, dump)

    def __str__(self):
        if len(type(self)._dims) > 1:
            params = ', '.join(f'{item.__repr__(False)}' for item in self)
        else:
            params = ', '.join(f'{item!r}' for item in self)
        return f'[{params}]'

    def __repr__(self, outer_level=True):
        if outer_level:
            return f'{type(self).__qualname__}({self})'
        else:
            return str(self)

    def __setitem__(self, index, item):
        # FUTURE: add mechanism to keep track of index for arrays
        cls = type(self)
        item_cls = cls._item_cls

        if isinstance(index, slice):
            items = list(item)
            replace_count = len(self[index])
            if len(items) != replace_count:
                raise ValueError(f'{cls.__qualname__!r} object does not support resizing')
            for i, item in enumerate(items):
                if type(item) is not item_cls:
                    items[i] = item_cls(item)
            item = items

        else:
            if type(item) is not item_cls:
                item = item_cls(item)

        list.__setitem__(self, index, item)

    def append(self, item):
        cls = type(self)
        raise TypeError(f'{cls.__qualname__!r} object does not support resizing)')

    def clear(self):
        cls = type(self)
        raise TypeError(f'{cls.__qualname__!r} object does not support resizing)')

    def extend(self, iterable):
        cls = type(self)
        raise TypeError(f'{cls.__qualname__!r} object does not support resizing)')

    def insert(self, index, item):
        cls = type(self)
        raise TypeError(f'{cls.__qualname__!r} object does not support resizing)')

    def pop(self, index=-1):
        cls = type(self)
        raise TypeError(f'{cls.__qualname__!r} object does not support resizing)')

    def remove(self, value):
        cls = type(self)
        raise TypeError(f'{cls.__qualname__!r} object does not support resizing)')
