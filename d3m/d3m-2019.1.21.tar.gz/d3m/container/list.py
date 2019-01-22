import datetime
import typing

import numpy  # type: ignore
import pandas  # type: ignore

from d3m import deprecate
from d3m.metadata import base as metadata_base

# See: https://gitlab.com/datadrivendiscovery/d3m/issues/66
try:
    from pyarrow import lib as pyarrow_lib  # type: ignore
except ModuleNotFoundError:
    pyarrow_lib = None

__all__ = ('List',)

L = typing.TypeVar('L', bound='List')


class List(list):
    """
    Extended Python standard `list` with the ``metadata`` attribute.

    You should use only standard data and container types as its elements.

    Metadata attribute is immutable, so if you ``update`` it, you should reassign it back::

        l.metadata = l.metadata.update(...)

    `List` is mutable, but this can introduce issues during runtime if a primitive
    modifies its inputs directly. Callers of primitives are encouraged
    to make it immutable to assure such behavior is detected/prevented,
    and primitives should copy inputs to a mutable `List` before modifying it.

    Parameters
    ----------
    iterable : Iterable
        Optional initial values for the list.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the list, or top-level metadata to be updated
        if ``iterable`` is another instance of this list class.
    generate_metadata: bool
        Automatically generate and update the metadata.
    check : bool
        Check if data matches the metadata. DEPRECATED: argument ignored.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference. DEPRECATED: argument ignored.
    timestamp : datetime
        A timestamp of initial metadata. DEPRECATED: argument ignored.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the list.
    """

    @deprecate.arguments('source', 'timestamp', 'check')
    def __init__(self, iterable: typing.Iterable = (), metadata: typing.Dict[str, typing.Any] = None, *,
                 generate_metadata: bool = True, check: bool = True, source: typing.Any = None,
                 timestamp: datetime.datetime = None) -> None:
        if isinstance(iterable, pandas.DataFrame):
            super().__init__(type(self)(row) for row in iterable.itertuples(index=False, name=None))
        else:
            if isinstance(iterable, numpy.matrix):
                # One cannot iterate over a matrix segment by segment. You always get back
                # a matrix (2D structure) and not an array of rows or columns. By converting
                # it to an array such iteration segment by segment works.
                iterable = numpy.array(iterable)
            super().__init__(iterable)

        from d3m import types

        if isinstance(iterable, types.Container):
            if isinstance(iterable, List):
                # We made a copy, so we do not have to generate metadata.
                self.metadata = iterable.metadata.set_for_value(self, generate_metadata=False)
            else:
                self.metadata = iterable.metadata.set_for_value(self, generate_metadata=generate_metadata)

            if metadata is not None:
                self.metadata = self.metadata.update((), metadata)
        else:
            self.metadata: metadata_base.DataMetadata = metadata_base.DataMetadata(metadata, for_value=self, generate_metadata=generate_metadata)

    def copy(self: L) -> L:
        # Metadata is copied from provided iterable.
        return type(self)(iterable=self)

    @typing.overload  # type: ignore
    def __getitem__(self, i: int) -> typing.Any:
        ...

    def __getitem__(self: L, s: slice) -> L:  # type: ignore
        if isinstance(s, slice):
            lst = type(self)(iterable=super().__getitem__(s))
            # TODO: We could do a slice in metadata as well?
            #       Update dimensions. Slice per-element metadata.
            lst.metadata = self.metadata.set_for_value(lst, generate_metadata=False)
            return lst
        else:
            return super().__getitem__(s)

    def __add__(self: L, x: typing.List) -> L:
        lst = type(self)(iterable=super().__add__(x))
        # TODO: We could do add in metadata as well?
        #       Update dimensions. Maybe x is List and has metadata.
        #       What to do if both have conflicting ALL_ELEMENTS metadata?
        lst.metadata = self.metadata.set_for_value(lst, generate_metadata=False)
        return lst

    def __iadd__(self: L, x: typing.Iterable) -> L:
        super().__iadd__(x)
        # TODO: We could do add in metadata as well?
        #       Update dimensions. Maybe x is List and has metadata.
        #       What to do if both have conflicting ALL_ELEMENTS metadata?
        return self

    def __mul__(self: L, n: int) -> L:
        lst = type(self)(iterable=super().__mul__(n))
        # TODO: We could do multiply in metadata as well?
        #       Update dimensions. Multiplicate per-element metadata.
        lst.metadata = self.metadata.set_for_value(lst, generate_metadata=False)
        return lst

    def __rmul__(self: L, n: int) -> L:
        lst = type(self)(iterable=super().__rmul__(n))
        # TODO: We could do multiply in metadata as well?
        #       Update dimensions. Multiplicate per-element metadata.
        lst.metadata = self.metadata.set_for_value(lst, generate_metadata=False)
        return lst

    def __setstate__(self, state: dict) -> None:
        self.__dict__ = state

        # During deep-copying metadata is not available in state in all calls to this method.
        if hasattr(self, 'metadata'):
            self.metadata = self.metadata.set_for_value(self, generate_metadata=False)

    def __reduce__(self) -> typing.Tuple[typing.Callable, typing.Tuple, dict]:
        reduced = super().__reduce__()
        return reduced


def list_serializer(obj: List) -> dict:
    data = {
        'metadata': obj.metadata,
        'list': list(obj),
    }

    if type(obj) is not List:
        data['type'] = type(obj)

    return data


def list_deserializer(data: dict) -> List:
    data_list = data.get('type', List)(data['list'])
    data_list.metadata = data['metadata'].set_for_value(data_list, generate_metadata=False)
    return data_list


if pyarrow_lib is not None:
    pyarrow_lib._default_serialization_context.register_type(
        List, 'd3m.list',
        custom_serializer=list_serializer,
        custom_deserializer=list_deserializer,
    )
