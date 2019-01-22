import datetime
import typing

import numpy  # type: ignore
import pandas  # type: ignore
from pandas.core.dtypes import common as pandas_common  # type: ignore

from . import list as container_list
from d3m import deprecate
from d3m.metadata import base as metadata_base

# See: https://gitlab.com/datadrivendiscovery/d3m/issues/66
try:
    from pyarrow import lib as pyarrow_lib  # type: ignore
except ModuleNotFoundError:
    pyarrow_lib = None

__all__ = ('DataFrame',)

# This implementation is based on these guidelines:
# https://pandas.pydata.org/pandas-docs/stable/internals.html#subclassing-pandas-data-structures

D = typing.TypeVar('D', bound='DataFrame')

Data = typing.Union[typing.Sequence, typing.Mapping]


# We have to convert our container "List" to regular list because Pandas do not accept list
# subclasses. See: https://github.com/pandas-dev/pandas/issues/21226
def convert_lists(data: Data = None) -> typing.Optional[Data]:
    if isinstance(data, list) and len(data):
        if isinstance(data, container_list.List):
            data = list(data)
        if isinstance(data, list) and isinstance(data[0], container_list.List):
            data = [list(row) for row in data]

    return data


def convert_ndarray(data: Data = None) -> typing.Optional[Data]:
    """
    If ndarray has more than 2 dimensions, deeper dimensions are converted to stand-alone numpy arrays.
    """

    if isinstance(data, numpy.ndarray) and len(data.shape) > 2:
        outer_array = numpy.ndarray(shape=(data.shape[0], data.shape[1]), dtype=numpy.object)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                # This retains the type, so if "data" is a container "ndarray", then also "data[i, j]" is.
                outer_array[i, j] = data[i, j]

        return outer_array

    return data


class DataFrame(pandas.DataFrame):
    """
    Extended `pandas.DataFrame` with the ``metadata`` attribute.

    Parameters
    ----------
    data : Data
        Anything array-like to create an instance from.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the data frame, or top-level metadata to be updated
        if ``data`` is another instance of this data frame class.
    index : Union[Index, Data]
        Index to use for resulting frame.
    columns : Union[Index, Data]
        Column labels to use for resulting frame.
    dtype : Union[dtype, str, ExtensionDtype]
        Data type to force.
    copy : bool
        Copy data from inputs.
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
        Metadata associated with the data frame.
    """

    @property
    def _constructor(self) -> type:
        return DataFrame

    @deprecate.arguments('source', 'timestamp', 'check')
    def __init__(self, data: Data = None, metadata: typing.Dict[str, typing.Any] = None, index: typing.Union[pandas.Index, Data] = None,
                 columns: typing.Union[pandas.Index, Data] = None, dtype: typing.Union[numpy.dtype, str, pandas_common.ExtensionDtype] = None, copy: bool = False, *,
                 generate_metadata: bool = True, check: bool = True, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        # If not a constructor call to this exact class, then a child constructor
        # is responsible to call a pandas constructor.
        if type(self) is DataFrame:
            pandas.DataFrame.__init__(self, data=convert_ndarray(convert_lists(data)), index=index, columns=columns, dtype=dtype, copy=copy)

        # Importing here to prevent import cycle.
        from d3m import types

        if isinstance(data, types.Container):  # type: ignore
            if isinstance(data, DataFrame):
                # We made a copy, so we do not have to generate metadata.
                self.metadata: metadata_base.DataMetadata = data.metadata.set_for_value(self, generate_metadata=False)  # type: ignore
            else:
                self.metadata: metadata_base.DataMetadata = data.metadata.set_for_value(self, generate_metadata=generate_metadata)  # type: ignore

            if metadata is not None:
                self.metadata: metadata_base.DataMetadata = self.metadata.update((), metadata)
        else:
            self.metadata: metadata_base.DataMetadata = metadata_base.DataMetadata(metadata, for_value=self, generate_metadata=generate_metadata)

    def __finalize__(self: D, other: typing.Any, method: str = None, **kwargs: typing.Any) -> D:
        self = super().__finalize__(other, method, **kwargs)

        # Merge operation: using metadata of the left object.
        if method == 'merge':
            obj = other.left
        # Concat operation: using metadata of the first object.
        elif method == 'concat':
            obj = other.objs[0]
        else:
            obj = other

        if isinstance(obj, DataFrame):
            # TODO: We could adapt (if this is after a slice) metadata instead of just copying?
            self.metadata: metadata_base.DataMetadata = obj.metadata.set_for_value(self, generate_metadata=False)
        # "metadata" attribute should already be set in "__init__",
        # but if we got here without it, let's set it now.
        elif not hasattr(self, 'metadata'):
            self.metadata: metadata_base.DataMetadata = metadata_base.DataMetadata(for_value=self)

        return self

    def __getstate__(self) -> dict:
        state = super().__getstate__()

        state['metadata'] = self.metadata

        return state

    def __setstate__(self, state: dict) -> None:
        super().__setstate__(state)

        self.metadata = state['metadata'].set_for_value(self, generate_metadata=False)


typing.Sequence.register(pandas.DataFrame)  # type: ignore


def dataframe_serializer(obj: DataFrame) -> dict:
    data = {
        'metadata': obj.metadata,
        'pandas': pandas.DataFrame(obj),
    }

    if type(obj) is not DataFrame:
        data['type'] = type(obj)

    return data


def dataframe_deserializer(data: dict) -> DataFrame:
    df = data.get('type', DataFrame)(data['pandas'])
    df.metadata = data['metadata'].set_for_value(df, generate_metadata=False)
    return df


if pyarrow_lib is not None:
    pyarrow_lib._default_serialization_context.register_type(
        DataFrame, 'd3m.dataframe',
        custom_serializer=dataframe_serializer,
        custom_deserializer=dataframe_deserializer,
    )
