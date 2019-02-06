# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from .._plumclass import PlumClass
from ._bitfield import BitField


class BitsClass(PlumClass):

    def __new__(mcs, name, bases, namespace, nbytes=None, byteorder=None, fill=None):
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, nbytes=None, byteorder=None, fill=None):
        super().__init__(name, bases, namespace)

        if nbytes is None:
            nbytes = cls._nbytes

        if byteorder is None:
            byteorder = cls._byteorder

        assert byteorder in {'big', 'little'}

        if fill is None:
            fill = cls._fill

        fields = dict()
        for name, typ in getattr(cls, '__annotations__', {}).items():
            field = getattr(cls, name, None)
            assert isinstance(field, BitField)
            field.type = typ
            field.name = name
            assert field.name == name
            fields[name] = field

        cls._byteorder = byteorder
        cls._fields = fields
        cls._fill = fill
        cls._nbytes = nbytes
