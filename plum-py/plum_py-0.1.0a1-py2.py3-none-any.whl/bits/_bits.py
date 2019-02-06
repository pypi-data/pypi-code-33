# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from .._plum import Plum
from ._bitsclass import BitsClass


class Bits(Plum, metaclass=BitsClass, nbytes=4, byteorder='little', fill=0):

    # filled in by metaclass
    _byteorder = 'little'
    _nbytes = 4
    _fill = 0
    _fields = dict()
    _max = 0xffffffff

    # TODO add ignore (mask) class attribute for comparison purposes??
    # TODO add ignore property to bitfield for this purpose?

    def __init__(self, *args, **kwargs):
        cls = type(self)

        if args or not kwargs:
            value = int(*args, **kwargs)

            if (value < 0) or (value > cls._max):
                raise ValueError(
                    f'{cls.__qualname__} requires 0 <= number <= {cls._max}')

            self._value = value

        else:
            fields = cls._fields

            self._value = cls._fill

            extras = set(kwargs) - set(fields)

            if extras:
                s = 's' if len(extras) > 1 else ''
                message = (
                    f'{cls.__qualname__}() '
                    f'got {len(extras)} unexpected keyword argument{s} ')
                message += ', '.join(repr(e) for e in fields if e in extras)
                raise TypeError(message)

            values = [kwargs.get(n, f.default) for n, f in fields.items()]
            missing = [n for n, v in zip(fields, values) if v is None]

            if missing:
                s = 's' if len(missing) > 1 else ''
                message = (
                    f'{cls.__qualname__}() '
                    f'missing {len(missing)} required keyword-only argument{s} ')
                message += ', '.join(missing)
                raise TypeError(message)

            for field, value in zip(fields.values(), values):
                field.__set__(self, value)

    @classmethod
    def __unpack__(cls, memory, dump):
        nbytes = cls._nbytes
        buffer = memory.getbytes(nbytes, type=cls, dump=dump)
        value = int.from_bytes(buffer, cls._byteorder, signed=False)

        self = cls.__new__(cls, value)
        cls.__init__(self, value)

        if dump:
            dump.value = self._value
            cls._add_bitfields_to_dump(self, dump)

        return self

    @classmethod
    def __pack__(cls, value, dump):
        if isinstance(value, cls):
            value = value._value
        elif isinstance(value, dict):
            value = cls(**value)._value
        elif not isinstance(value, int):
            raise TypeError(f'value must be int, dict, or {cls.__qualname__}')

        bytes_ = value.to_bytes(cls._nbytes, cls._byteorder, signed=False)

        if dump:
            dump.value = str(value)
            dump.memory = bytes_
            dump.cls = cls
            cls._add_bitfields_to_dump(value, dump)

        yield bytes_

    @classmethod
    def _add_bitfields_to_dump(cls, value, dump):
        for name, field in cls._fields.items():
            row = dump.add_level(
                access='.' + name,
                bits=(field.pos, field.size))
            # TODO deal with bit numbers
            row.value = str(getattr(cls, name).__get__(value, cls))
            row.cls = field.type.__qualname__

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        params = ', '.join(f'{n}={getattr(self, n)!r}' for n in self._fields)
        return f'{type(self).__qualname__}({params})'

    def __int__(self):
        return int(self._value)

    def __eq__(self, other):
        return self.__int__() == int(other)
