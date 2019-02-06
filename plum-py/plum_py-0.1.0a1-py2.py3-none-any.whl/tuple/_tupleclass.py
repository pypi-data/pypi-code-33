from .._functions import calcsize
from .._plumclass import PlumClass


class TupleClass(PlumClass):

    def __new__(mcs, name, bases, namespace, types=None):
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, types=None):
        super().__init__(name, bases, namespace)

        if types is None:
            types = cls._types

        nbytes = 0
        for typ in types:
            try:
                nbytes += calcsize(typ)
            except SizeError:
                nbytes = None
                break

        cls._nbytes = nbytes
        cls._types = types
