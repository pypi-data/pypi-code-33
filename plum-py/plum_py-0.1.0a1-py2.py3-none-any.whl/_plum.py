# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Plum:

    """Packable/Unpacked Memory base class."""

    _nbytes = -1

    @classmethod
    def __unpack__(cls, memory, dump):
        raise NotImplementedError(f'{cls.__qualname__!r} does not support plum.unpack( )')

    @classmethod
    def __pack__(cls, value, dump):
        raise NotImplementedError(f'{cls.__qualname__!r} does not support plum.pack( )')

    def __repr__(self):
        cls = type(self)
        return f'{type(self).__qualname__}({cls.__str__(self)})'
