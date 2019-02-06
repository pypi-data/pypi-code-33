# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from .._plum import Plum
from ._structureclass import StructureClass


class Structure(dict, Plum, metaclass=StructureClass):

    # filled in by metaclass
    _members = dict()
    _nbytes = 0

    @classmethod
    def __unpack__(cls, memory, dump):
        if dump:
            dump.cls = cls

            self = dict.__new__(cls)
            dict.__init__(self)
            for name, member in cls._members.items():
                subdump = dump.add_level(access=f'.{name}')
                self[member.name] = member.get_cls(self).__unpack__(memory, subdump)
        else:
            self = dict.__new__(cls)
            dict.__init__(self)
            for name, member in cls._members.items():
                self[member.name] = member.get_cls(self).__unpack__(memory, dump)

        return self

    @classmethod
    def __pack__(cls, members, dump):
        if not isinstance(members, cls):
            members = cls(members)

        if dump:
            dump.cls = cls

            for name, value in members.items():
                yield from value.__pack__(value, dump.add_level(access=f'.{name}'))
        else:
            for value in members.values():
                yield from value.__pack__(value, dump)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        params = ', '.join(f'{n}={self[n]!r}' for n in self._members)
        return f'{type(self).__qualname__}({params})'

    def __setitem__(self, key, value):
        member = type(self)._members[key]
        member_cls = member.get_cls(self)
        if type(value) is not member_cls:
            value = member_cls(value)
        dict.__setitem__(self, key, value)

    # TODO - implement ignores with compares
