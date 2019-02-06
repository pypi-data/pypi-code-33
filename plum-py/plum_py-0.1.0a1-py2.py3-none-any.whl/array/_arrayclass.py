# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from .._functions import calcsize, SizeError
from .._plum import Plum
from .._plumclass import PlumClass


GREEDY_DIMS = tuple()


class ArrayInitError(Exception):
    pass


class ArrayClass(PlumClass):

    def __new__(mcs, name, bases, namespace, item_cls=None, dims=None):
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, item_cls=None, dims=None):
        super().__init__(name, bases, namespace)

        if item_cls is None:
            item_cls = cls._item_cls

        assert issubclass(item_cls, Plum)

        if dims is None:
            dims = cls._dims

        dims = tuple(int(d) for d in dims)
        assert all(d > 0 for d in dims)

        if len(dims) > 1:
            item_cls = ArrayClass('Array', bases, {}, item_cls, dims[1:])

        if dims == GREEDY_DIMS:
            nbytes = -1
        else:
            try:
                nbytes = calcsize(item_cls)
            except SizeError:
                nbytes = -1
            else:
                nbytes *= dims[0]

        cls._dims = dims
        cls._item_cls = item_cls
        cls._nbytes = nbytes

    @classmethod
    def _make_instance(cls, iterable, index):
        self = list.__new__(cls, iterable)
        list.__init__(self, iterable)

        dims = cls._dims

        if (dims != GREEDY_DIMS) and (len(self) != dims[0]):
            invalid_dimension = (
                f'expected length of item{index} to be {dims[0]} '
                f'but instead found {len(self)}')
            raise ArrayInitError(invalid_dimension)

        item_cls = cls._item_cls
        item_cls_is_this_type = isinstance(item_cls, ArrayClass)

        for i, item in enumerate(self):
            if type(item) is not item_cls:
                try:
                    if item_cls_is_this_type:
                        self[i] = item_cls(item)
                    else:
                        self[i] = item_cls(item, index + f'[{i}]')
                except ArrayInitError:
                    # allow lowest level one to propagate
                    raise
                except Exception as exc:
                    raise ArrayInitError(
                        f"unexpected {type(exc).__qualname__!r} "
                        f"exception occurred during array initialization, "
                        f"item{index}[{i}] did not successfully convert to a "
                        f"{item_cls.__qualname__!r}, original exception "
                        f"traceback appears above this exception's traceback"
                    ).with_traceback(exc.__traceback__)

        return self

    def __call__(cls, iterable=()):
        return cls._make_instance(iterable, '')
