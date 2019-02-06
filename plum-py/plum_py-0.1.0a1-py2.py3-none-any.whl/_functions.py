# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from ._dump import Dump
from ._memory import Memory
from ._plum import Plum
from ._plumclass import PlumClass


class PackError(Exception):

    """Pack operation error."""

    pass


class SizeError(Exception):
    pass


def calcsize(*items):
    """Get size of view (in bytes).

    :param items: plum class or instance
    :type items: PlumClass or Plum
    :returns: size in bytes
    :rtype: int
    :raises SizeError: if size varies with instance

    For example:
    >>> from plum.int.little import UInt16
    >>> calcsize(UInt16)
    2
    >>> calcsize(UInt16(0))
    2
    >>> calcsize(UInt8, UInt16)
    3

    """
    nbytes = 0

    for i, item in enumerate(items):
        if isinstance(item, Plum):
            item_nbytes = type(item)._nbytes
            if item_nbytes < 0:
                try:
                    # attempt w/o dump for performance
                    item_nbytes = len(_pack((item,), {}, None))
                except Exception:
                    # do it over to include dump in exception message
                    item_nbytes = len(_pack((item,), {}, Dump(access=f'[{i}]')))
                    raise RuntimeError(f'error in __pack__ implementation for item {i}')

        elif isinstance(item, PlumClass):
            item_nbytes = item._nbytes
            if item_nbytes < 0:
                raise SizeError(f'{item.__qualname__!r} instance sizes vary')

        else:
            raise TypeError(f'{item!r} is not a plum class or instance')

        nbytes += item_nbytes

    return nbytes


def dump(item):
    """Print packed memory summary.

    :param Plum item: packable/unpacked memory item

    """
    print(getdump(item))


def getdump(item):
    """Produce packed memory summary.

    :param Plum item: packable/unpacked memory item
    :param str name: item name (for ``access`` column)
    :returns: summary table of view detailing memory bytes and layout
    :rtype: str

    """
    dump = Dump()
    _pack((item,), {}, dump)
    dump.access = 'x'
    return dump.get_table()


'''
def getvalue(view):
    """Convert view into Python built-in form.

    For example, convert a unsigned 16 bit integer
    data memory view to a native Python ``int``:
        >>> from plum.int.le import UInt16
        >>> x = UInt16(0)
        >>> x
        UInt16(0)
        >>> getvalue(x)
        0

    :param Plum view: data memory view
    :returns: value in Python built-in form
    :rtype: object (Python built-in forms)

    """
    return view.__getvalue__()


def initialize(view, *args, **kwargs):
    """Reset data memory view with initializer arguments.

    Set view value and corresponding memory bytes to new
    value using constructor (__init__) arguments.
    For example:

        >>> from plum import initialize
        >>> from plum.int.le import UInt8, UInt16
        >>> x = UInt16('11', base=16)
        >>> x
        UInt16(17)
        >>> initialize(x, 'ff', base=16)
        >>> x
        UInt16(255)

    :param tuple args: initializer positional arguments
    :param dict kwargs: initializer keyword arguments

    """
    view.__initialize__(*args, **kwargs)
'''


def _pack(items, kwargs, dmp):
    pieces = []
    try:
        cls = None
        i = 0
        for item in items:
            if isinstance(item, PlumClass):
                if cls is None:
                    cls = item
                else:
                    raise TypeError('missing positional argument, class specified without a value')
            else:
                if cls is None:
                    cls = type(item)
                if dmp:
                    if dmp.access:
                        dmp = dmp.add_row(access=f'[{i}]')
                    else:
                        dmp.access = f'[{i}]'
                pieces.extend(cls.__pack__(item, dmp))
                i += 1
                cls = None

        if cls is not None:
            raise TypeError('missing positional argument, class specified without a value')

        if kwargs:
            for name, item in kwargs.items():
                if dmp:
                    if dmp.access:
                        dmp = dmp.add_row(access=name)
                    else:
                        dmp.access = name
                pieces.extend(item.__pack__(item, dmp))

    except Exception as exc:
        if dmp:
            raise PackError(
                f"\n\n{dmp.get_table() if dmp else '<no dump table yet>'}"
                f"\n\nPackError: unexpected {type(exc).__qualname__} "
                f"exception occurred during pack operation, dump "
                f"above shows interrupted progress, original "
                f"exception traceback appears above this exception's "
                f"traceback"
            ).with_traceback(exc.__traceback__)
        else:
            raise

    return b''.join(pieces)


def pack_and_getdump(*items, **kwargs):
    """Pack items into byte sequence and get packed memory summary.

    For example:

        >>> from plum import pack
        >>> from plum.int.little import UInt8, UInt16
        >>> pack(UInt8(1), UInt16(2))
        b'010200'
        >>> pack(UInt8, 1, UInt16, 2)
        b'010200'
        >>> pack(m1=UInt8(1), m2=UInt16(2))
        b'010200'

    :param items: packable/unpacked memory items
    :type items: tuple of plum types/values
    :param kwargs: packable/unpacked memory items
    :type kwargs: dict of plum instances

    """
    dmp = Dump()
    return _pack(items, kwargs, dmp), dmp.get_table()


def pack(*items, **kwargs):
    """Pack items into byte sequence.

    For example:

        >>> from plum import pack
        >>> from plum.int.le import UInt8, UInt16
        >>> pack(UInt8(1), UInt16(2))
        b'010200'
        >>> pack(UInt8, 1, UInt16, 2)
        b'010200'
        >>> pack(m1=UInt8(1), m2=UInt16(2))
        b'010200'

    :param items: packable/unpacked memory items
    :type items: Plum (e.g. UInt8, Array, etc.)
    :param kwargs: packable/unpacked memory items
    :type kwargs: dict of plum instances

    """
    try:
        # attempt w/o dump for performance
        return _pack(items, kwargs, dmp=None)
    except Exception:
        # do it over to include dump in exception message
        _pack(items, kwargs, Dump())
        raise RuntimeError('error in __pack__ implementation for one of the types used')


'''
def setvalue(view, value):
    """Pack value into view data memory.

    For example:
        >>> from plum import setvalue
        >>> from plum.int.le import UInt16
        >>> x = UInt16(0)
        >>> x.setvalue(255)
        >>> x
        UInt16(255)

    :param Plum view: data memory view
    :param object value: new value

    """
    view.__setvalue__(value)
'''


def unpack_and_getdump(cls, buffer):
    """Unpack memory bytes and get packed memory summary.

    For example:
        >>> from plum import unpack
        >>> from plum.int.little import UInt8, UInt16
        >>> unpack(UInt16, b'0102')
        UInt16(513)

    :param Plum cls: plum type, e.g. ``UInt16``
    :param bytes-like buffer: packed memory bytes
    :returns: tuple of (plum instance, summary)
    :rtype: (cls, str)

    """
    memory = Memory(buffer)
    return memory.unpack_and_getdump(cls)


def unpack(cls, buffer):
    """CUnpack memory bytes.

    For example:
        >>> from plum import unpackfast
        >>> from plum.int.little import UInt8, UInt16
        >>> unpackfast(UInt16, b'0102')
        UInt16(513)

    :param Plum cls: plum type, e.g. ``UInt16``
    :param bytes-like buffer: packed memory bytes
    :returns: plum instance
    :rtype: cls

    """
    memory = Memory(buffer)

    try:
        with memory:
            return cls.__unpack__(memory, None)
    except Exception:
        # do it over to include dump in exception message
        memory.cursor = 0
        memory.unpack_and_getdump(cls)
        assert 0, "Internal Error"

'''
def view(type, memory, offset):
    """Create view of packed memory bytes.

    For example:
        >>> from plum import Memory, view
        >>> from plum.int.le import UInt8
        >>> memory = Memory(b'001100')
        >>> view(UInt16, memory, offset=1)
        UInt8(17)

    """
    assert isinstance(memory, Memory)
    return type.__new_view__(memory, offset)
'''
