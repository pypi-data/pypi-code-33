# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from enum import IntEnum

from .._plumclass import PlumClass


class IntClass(PlumClass):

    def __new__(mcs, name, bases, namespace, nbytes=None, signed=None, byteorder=None, enum=None):
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, nbytes=None, signed=None, byteorder=None, enum=None):
        super().__init__(name, bases, namespace)

        if nbytes is None:
            nbytes = cls._nbytes

        nbytes = int(nbytes)

        assert nbytes > 0

        if signed is None:
            signed = cls._signed

        signed = bool(signed)

        if byteorder is None:
            byteorder = cls._byteorder

        assert byteorder in {'big', 'little'}

        if signed:
            minvalue = -(1 << (nbytes * 8 - 1))
            maxvalue = (1 << (nbytes * 8 - 1)) - 1
        else:
            minvalue = 0
            maxvalue = (1 << (nbytes * 8)) - 1

        if enum is None:
            enum = cls._enum_cls

        assert enum is None or issubclass(enum, IntEnum)

        cls._byteorder = byteorder
        cls._enum_cls = enum
        cls._max = maxvalue
        cls._min = minvalue
        cls._nbytes = nbytes
        cls._signed = signed
