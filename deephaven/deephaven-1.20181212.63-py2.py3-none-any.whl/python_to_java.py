#
# Copyright (c) 2016-2017 Deephaven and Patent Pending
#

import jpy
import numpy as np
import pandas as pd
import sys
import time
import warnings

from illumon.iris import TableTools
from .constants import dtype_to_columnsource_and_type, java_array_types

__object_column_source__ = 'com.illumon.iris.db.v2.sources.immutable.ImmutableObjectArraySource'

def _is_object_column_source(source):
    return source == __object_column_source__

def df_to_table(df):
    if isinstance(df, pd.DataFrame):
        if isinstance(df.index, pd.core.index.MultiIndex):
            raise ValueError("MultiIndexed DataFrames not supported")
        return _pandasdf_to_table(df)
    raise RuntimeError("Unsupported data frame %s" % type(df))


def _pandasdf_to_table(df):
    column_source = []
    column_names = list(df)

    for i in range(0, len(column_names)):
        column_source.append(_create_column_source_(df.get(column_names[i])))

    # noinspection PyPep8Naming
    Arrays = jpy.get_type("java.util.Arrays")

    return TableTools.newTable(len(df), Arrays.asList(column_names), Arrays.asList(column_source))


def _create_column_source_(series):
    is_array_source = False
    type_ = series.dtype.name
    array_ = series.values

    if type_.startswith("datetime64"):
        types = dtype_to_columnsource_and_type.get(type_, (
            'com.illumon.iris.db.v2.sources.immutable.ImmutableDateTimeArraySource', 'long'))
        array_ = array_.astype('int64')

    else:
        types = dtype_to_columnsource_and_type.get(type_, (__object_column_source__, 'java.lang.String'))

    col_source_class = jpy.get_type(types[0])
    java_type = types[1]

    try:
        if java_type == 'java.lang.String':
            array_ = np.where(np.equal(array_, None), array_, array_.astype(str))
            a = jpy.array(java_type, array_)
        else:
            a = jpy.array(java_type, array_)

    except ValueError:
        # Should only run into this ValueError if we try to process an iterable
        # Also, we only support 2d arrays and uniform types for now.

        warnings.warn("Attempting to process series %s with arrays/tuples. This may take a while" % series.name, FutureWarning)

        original_type = type_

        try:
            type_ = None

            # Our strategy to determine the type will be to pull the type of the first element of the first list
            # If that list is empty, we will try the next one
            # If all of the lists are empty, default to string for now

            row_index = 0
            while type_ is None:
                try: type_ = type(array_[row_index][0]).__name__
                finally: row_index += 1

                if row_index > len(array_):
                    type_ = "str"

            type_ = type_ if type_ in java_array_types else dtype_to_columnsource_and_type[type_][1]
            java_type = java_array_types[type_]

        except KeyError:
            raise TypeError("Unsupported column value type: " + original_type + ". Arrays must be uniform type and may not have nested lists or tuples")

        try:
            a = jpy.array(java_type, array_)
        except (ValueError,TypeError) as e:
            raise TypeError("Column arrays must be of uniform type to convert to table")


        if type_ == 'str': type_ = 'java.lang.String'
        java_class =  jpy.array(type_, []).getClass()

        is_array_source = True

    if _is_object_column_source(types[0]):
        if is_array_source:
            return col_source_class(a, java_class)
        else:
            typ_temp = jpy.get_type(java_type)
            return col_source_class(a, typ_temp().getClass())

    else:
        return col_source_class(a)

