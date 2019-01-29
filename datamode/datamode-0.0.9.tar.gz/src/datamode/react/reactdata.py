import json
import pandas as pd

# https://pandas.pydata.org/pandas-docs/stable/api.html#data-types-related-functionality
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype, is_string_dtype, is_bool_dtype

from .kde import KdeBuilder
from .stats import StatsBuilder, BARCHART_MAX_ITEMS
from datamode.utils.data import is_col_vector, is_basic_type

from datamode.utils.utils import get_logger
log = get_logger(__name__)

# Data management class to pick subsets of the existing dataset, especially for showing to React code.
class ReactData():
  def __init__(self, tcon, timer, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.tcon = tcon
    self.transforms = tcon.transforms
    self.timer = timer

    # Cache to hold already-filtered dataframes.
    self.filtercache = {}

  def get_source_dataframe(self, transform_id):
    return self.tcon.ds.tstates[transform_id].get_working_df()

  def get_df_dest_at_transform_id(self, transform_id):
    return self.tcon.ds.tstates[transform_id].dest_tables[0]

  def get_filtercache_key(self, transform_id, facets):
    return str(transform_id) + json.dumps(facets)

  def get_filtered_df(self, transform_id, facets, sort=None, rowset=None):
    key = self.get_filtercache_key(transform_id, facets)
    df = self.get_df(key, transform_id, facets)

    if sort:
      df = self.sort_df(key, df, transform_id, facets, sort)

    # rowset only applies to the filtered rows, not the entire dataframe.
    # So we have to subset the df after initial filtering.
    # Todo: implement some kind of cache for the filter because otherwise it will happen at every scroll.
    if rowset is not None:
      index_start = rowset['index_start']
      index_end = rowset['index_end']
      df = df[index_start : index_end + 1]

      # log.debug(f'rowset={rowset}, count={df.shape[0]}')

    return df

  def get_df(self, key, transform_id, facets):
    df = self.filtercache.get(key)
    if df is None:
      df = self.build_filtered_df(transform_id, facets)
      self.filtercache[key] = df
      log.debug(f'Filtercache build on key={key}')
    else:
      log.debug(f'Filtercache hit on key={key}')
      pass

    # Make a copy so that we can modify the new dataframe without changing the cache.
    # Note: this will not copy the underlying objects, just references to them.
    df = df.copy(deep=True)

    return df


  # Sorts the dataframe and stores it in the cache as well.
  def sort_df(self, filtercache_key, df, transform_id, facets, sort):
    if len(sort['sortBy']) == 0:
      return df

    sort_by = sort['sortBy'][0]
    sort_directions = sort['sortDirection']

    # If the sort_by isn't present, bail.
    if sort_by not in df.columns:
      return

    ascending = sort_directions[sort_by] == 'ASC'
    na_position = 'first' if ascending else 'last'
    df.sort_values(sort_by, ascending=ascending, inplace=True, na_position=na_position)

    # Update the filtercache
    self.filtercache[filtercache_key] = df
    return df


  def build_filtered_df(self, transform_id, facets):
    df_source = self.get_source_dataframe(transform_id)
    df = df_source.copy(deep=True)

    # Build a new faceted dataframe - facets are ANDed together
    # Each facet can be:
    #   None -> show all Nones  (nulls in JS of course)
    #   List of two items -> filter by range
    #   Single value - filter the single value only.
    for colname, entry in facets.items():

      # We can't filter columns that aren't present in the current df.
      # This can happen if the user applies a filter, then clicks on a previous frame that doesn't have that column.
      if colname not in df.columns:
        continue

      # Special handling for a raw None value (null in JS)
      if entry is None:
        df = df.loc[ df[colname].isnull() ]  # Filter by null values

      # Dictionary - later on, can be used for explicit NOT filters as well
      elif type(entry) is dict and 'isnull' in entry:
        if entry['isnull']:
          df = df.loc[ df[colname].isnull() ]  # Filter by null values
        else:
          df = df.loc[ df[colname].notnull() ]  # Filter by nonnull values

      # Range
      elif type(entry) is list:
        mask_start = df[colname] > entry[0]
        mask_end = df[colname] <= entry[1]
        df = df.loc[ mask_start & mask_end ]

      # Single value
      elif is_basic_type(entry):
        df = df.loc[ df[colname] == entry ]  # Filter by basic type

      # Unsupported
      else:
        raise Exception(f'Facet colname={colname}, entry={entry} has unsupported type.' )

    return df


  def get_pretty_dtype(self, dtyp, col):
    if is_col_vector(col):
      return 'vector'
    if is_bool_dtype(dtyp):
      return 'boolean'
    elif is_numeric_dtype(dtyp):
      return 'numeric'
    elif is_datetime64_any_dtype(dtyp):
      return 'datetime'
    elif is_string_dtype(dtyp):
      return 'categorical'
    else:
      return 'unknown'


  def get_colinfos(self, transform_id, df, columnar_viz=None):
    # log.debug(f'get_colinfos transform_id={transform_id}, rows={df.shape[0]}')
    colnames = df.columns.tolist()
    source_cols, dest_cols = self.get_source_and_dest_cols(transform_id)

    # The UI defaults to no target, even if kde is selected.
    col_target = None
    kde_builder = None
    if columnar_viz['vizType'] == 'kde':
      target_variable = columnar_viz['targetVariable']
      col_target = df[target_variable] if target_variable else None
      log.debug(f'number of rows: {df.shape[0]}')
      kde_builder = KdeBuilder(df.shape[0], col_target)



    colinfos = []
    for colname in colnames:
      colinfo = self.build_single_colinfo(df, colname, source_cols, dest_cols, kde_builder)
      colinfos.append(colinfo)

    return colinfos


  def build_single_colinfo(self, df, colname, source_cols, dest_cols, kde_builder):
    col = df[colname]

    sb = StatsBuilder(col, colname, self.timer, kde_builder)
    stats = sb.build_column_stats()
    colviz_type = sb.colviz_type

    dtype = df[colname].dtype
    pretty_dtype = self.get_pretty_dtype(dtype, col)

    colinfo = {
      'colname': colname,
      'colviz_type': sb.colviz_type,
      'dtype': str(dtype),
      'pretty_dtype': pretty_dtype,
      'is_datetime': is_datetime64_any_dtype(dtype), # This could probably be computed higher up and cached
      'stats': stats,
      'source_col': colname in source_cols,
      'dest_col': colname in dest_cols,
    }

    # log.debug(f'colname={colname}, vector={is_col_vector(col)}, colviz_type={sb.colviz_type}')
    return colinfo


  def get_source_and_dest_cols(self, transform_id):
    tresult = self.tcon.ds.tstates[transform_id].result
    return list(tresult.set_source_cols), list(tresult.set_dest_cols)


def unpack_filterset(filterset):
  transform_id = filterset['transformId']
  facets = filterset.get('facets', {})  # Default to empty dict
  sort = filterset.get('sort', None)  # Default to None
  return transform_id, facets, sort
