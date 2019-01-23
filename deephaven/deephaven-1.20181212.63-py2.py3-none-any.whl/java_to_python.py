#
# Copyright (c) 2016-2017 Deephaven and Patent Pending
#

import numpy as np
import pandas as pd
import time
import jpy

from .constants import java_type_map, null_values

# assumes a table which is not ticking. Ticking tables may cause errors!
def frozen_table_to_df(t, convert_nulls=False, categoricals=None):
    import logging
    d = {}

    col_defs = t.getDefinition().getColumns()
    col_names = map(lambda col: col.getName(), col_defs)

    # TODO: Add checks for bad category types
    if categoricals is not None:
        for category in categoricals:
            if category not in col_names:
                raise ValueError("Specified category not found in table")

    for col_name in col_names:
        logging.info("Column %s get.....;" % (col_name))

        if categoricals and col_name in categoricals:
            d[col_name] = _handle_categorical(t,col_name,convert_nulls)

        else:
            col = t.getColumn(col_name)
            d[col_name] = column_to_series(col, convert_nulls)

    return pd.DataFrame(d)


# attempt at categorical optimization with mapping. Not sure if this is actually any faster than just converting the type
# TODO: Should probably also just add a check to make sure that we aren't doing this for primitive types because that would just be straight up slower
def _handle_categorical(t,col_name,convert_nulls):

    # TODO: numpy.unique(*, return_inverse=True) faster?

    col_id = col_name + "id"
    mapped_ids = t.selectDistinct(col_name).update(col_id + " = i")
    mapping = mapped_ids.getColumn(col_name).getDirect()

    t = t.naturalJoin(mapped_ids, col_name).renameColumns(col_id + "=" + col_name)
    col = t.getColumn(col_id)

    return column_to_series(col,convert_nulls).astype("category").cat.rename_categories(mapping)


def _is_dbarray(col_type):
    return col_type.find('dbarrays') != -1


def _is_array(col_type):
    return col_type.startswith('[')


def column_to_nparray(col, convert_nulls = False):
    col_type = col.getType().getName()
    curr_col = col.getDirect()

    null_type = null_values.get(col_type, None)

    if not convert_nulls and col_type in ['java.lang.Boolean', 'boolean'] and null_type in curr_col:
        raise ValueError("Null found in boolean column. Set convert_nulls flag to true to allow")

    if col_type == 'com.illumon.iris.db.tables.utils.DBDateTime':
        col = [None if cur is None else cur.getNanos() for cur in curr_col]
        return np.asarray(col).astype('datetime64[ns]')

    elif _is_dbarray(col_type):
        #TODO: might want explicit type casting here
        curr_col = [cur.toArray() for cur in curr_col]
        return [np.asarray(cur) for cur in curr_col]

    elif _is_array(col_type):
        return [np.asarray(cur) for cur in curr_col]

    else:
        python_type = java_type_map.get(col_type, np.object)
        return np.asarray(curr_col, dtype=python_type)


def column_to_series(col, convert_nulls=False):
    time_zone = time.tzname[0]
    col_type = col.getType().getName()

    nparray = _handle_nulls(column_to_nparray(col, convert_nulls), col_type, convert_nulls)

    if col_type == 'com.illumon.iris.db.tables.utils.DBDateTime':
        return pd.Series(nparray).dt.tz_localize('UTC').dt.tz_convert(time_zone)

    else:
        return pd.Series(nparray)


def _handle_nulls(nparray, col_type, convert_nulls):
    null_type = null_values.get(col_type, None)
    filtered = nparray

    if col_type in ['float', 'double'] and null_type in nparray:
        filtered = np.where(np.equal(nparray, null_type), np.nan, nparray)

    if convert_nulls:
        if col_type in ['int', 'long', 'short', 'byte'] and null_type in nparray:
            new_type = np.float64 if col_type == 'long' else np.float32
            newtypearray = nparray.astype(new_type)
            filtered = np.where(np.equal(newtypearray, null_type), np.nan, newtypearray)

    elif col_type in ['java.lang.Boolean', 'boolean'] and null_type in nparray:
        raise ValueError("Null found in boolean column. Set convert_nulls flag to true to allow")

    return filtered


def _getNamesAndTypes(t):
    return [(x.getName(),x.getType().getName()) for x in t.getColumns()]


def remote_table_to_df(remote_table, convert_nulls=False, categoricals=None ):
    d = {}

    namesAndTypes = _getNamesAndTypes(remote_table)

    bs = jpy.get_type("java.util.BitSet")(len(namesAndTypes))
    bs.set(0, len(namesAndTypes))

    snapshot = remote_table.getRemoteTableHandle().getDirect(bs)