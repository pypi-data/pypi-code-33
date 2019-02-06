# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from enum import IntEnum


class BitField:

    __slots__ = [
        '_mask',
        '_signbit',
        'default',
        'name',
        'pos',
        'size',
        'type',
    ]

    def __init__(self, pos, size, default, signed):

        pos = int(pos)
        size = int(size)
        signed = bool(signed)

        assert pos >= 0

        if signed:
            assert size > 1
            signbit = 1 << (size - 1)
        else:
            assert size > 0
            signbit = 0

        self._mask = (1 << size) - 1
        self._signbit = signbit

        self.default = default
        self.name = None  # assigned via __set_name__ protocol
        self.pos = pos
        self.size = size
        self.type = None  # assigned during Bits class construction (by BitsClass.__new__)

    @property
    def signed(self):
        return bool(self._signbit)

    def __repr__(self):
        return ('BitField('
                f'name={self.name!r},'
                f'type={self.type!r},'
                f'pos={self.pos!r},'
                f'size={self.size!r},'
                f'default={self.default!r},'
                f'signed={self.signed!r}'
                ')')

    def x__set_name__(self, owner, name):
        # assert self._name is None, 'bitfield definition already in use'
        self._name = name

    def __get__(self, obj, type=None):
        if obj is None:
            return self

        value = (int(obj) >> self.pos) & self._mask
        if self._signbit & value:
            # its a signed number and its negative
            value = -((1 << self.size) - value)

        try:
            return self.type(value)
        except ValueError:
            if issubclass(self.type, IntEnum):
                return value
            else:
                raise

    def __set__(self, obj, value):
        mask = self._mask
        size = self.size
        pos = self.pos

        if value & ~mask:
            if self._signbit:
                minvalue = -(1 << (size - 1))
                maxvalue = -(1 + minvalue)
            else:
                minvalue = 0
                maxvalue = (1 << size) - 1
            raise ValueError(f'bitfield {self.name!r} requires {minvalue} <= number <= {maxvalue}')

        obj._value = (obj._value & ~(mask << pos)) | ((value & mask) << pos)



# TODO: look at dataclass implementation as to why this should be a function
#       rather than just leaving user instantiate class directly
#       (has something to do with IDE introspection/hints)
def bitfield(*, pos, size, default=None, signed=False):
    """Create bit field definition.

    :param int pos: bit offset of least significant bit
    :param int size: size in bits
    :param int default: initial value when unspecified
    :param bool signed: interpret as signed integer
    :returns: bit field definition
    :rtype: BitField

    """
    return BitField(pos, size, default, signed)
