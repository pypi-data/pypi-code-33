# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from .._plum import Plum
from ._sequenceclass import SequenceClass


class Sequence(list, Plum, metaclass=SequenceClass):

    # filled in by metaclass
    _types = ()
    _nbytes = 0

    @classmethod
    def __unpack__(cls, memory, dump):
        self = list.__new__(cls)
        list.__init__(self)

        if dump:
            dump.cls = cls

            for i, item_cls in enumerate(cls._types):
                subdump = dump.add_level(access=f'[{i}]')
                list.append(self, item_cls.__unpack__(memory, subdump))
        else:
            for i, item_cls in enumerate(cls._types):
                list.append(self, item_cls.__unpack__(memory, None))

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
            for item in items:
                yield from item.__pack__(item, dump)

    def __str__(self):
        params = ', '.join(f'{item!r}' for item in self)
        return f'[{params}]'

    def __repr__(self):
        return f'{type(self).__qualname__}({self})'

    def __setitem__(self, index, item):
        cls = type(self)
        types = cls._types

        if isinstance(index, slice):
            items = list(item)
            if types:
                types = types[index]
                if len(items) != len(types):
                    raise ValueError(f'{cls.__qualname__!r} object does not support resizing')
                for i, (item, item_cls) in enumerate(items, types):
                    if type(item) is not item_cls:
                        items[i] = item_cls(item)
            else:
                for i, item in enumerate(items):
                    if not isinstance(item, Plum):
                        raise TypeError(f"slice item {i} must be a Plum subclass")
            item = items

        elif types:
            item_cls = types[index]
            if type(item) is not item_cls:
                item = item_cls(item)

        else:
            if not isinstance(item, Plum):
                raise TypeError(f"item must be a Plum subclass")

        list.__setitem__(self, index, item)

    def append(self, item):
        cls = type(self)
        types = cls._types

        if types:
            raise ValueError(f'{cls.__qualname__!r} object does not support resizing')

        if not isinstance(item, Plum):
            raise TypeError(f"item must be a Plum subclass")

        list.append(self, item)

    def clear(self):
        cls = type(self)
        types = cls._types

        if types:
            raise ValueError(f'{cls.__qualname__!r} object does not support resizing')

        list.clear(self)

    def extend(self, iterable):
        cls = type(self)
        types = cls._types

        if types:
            raise ValueError(f'{cls.__qualname__!r} object does not support resizing')

        for i, item in enumerate(iterable):
            if isinstance(item, Plum):
                list.append(self, item)
            else:
                raise TypeError(f"item {i} must be a Plum subclass")

    def insert(self, index, item):
        cls = type(self)
        types = cls._types

        if types:
            raise ValueError(f'{cls.__qualname__!r} object does not support resizing')

        if not isinstance(item, Plum):
            raise TypeError(f"item must be a Plum subclass")

        list.insert(self, index, item)

    def pop(self, index=-1):
        cls = type(self)
        types = cls._types

        if types:
            raise ValueError(f'{cls.__qualname__!r} object does not support resizing')

        return list.pop(self, index)

    def remove(self, value):
        cls = type(self)
        types = cls._types

        if types:
            raise ValueError(f'{cls.__qualname__!r} object does not support resizing')

        list.remove(self, value)
