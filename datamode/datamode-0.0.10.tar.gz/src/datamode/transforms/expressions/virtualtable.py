import pandas as pd

from .ops import apply_comparison_op

from datamode.utils.utils import get_logger
log = get_logger(__name__)


# Abstraction layer for the merged frankentable.
class VirtualTable():
  def __init__(self, working_dfs, single_table=None, tc_left_join=None, tc_right_join=None, *args, **kwargs):
    self.working_dfs = working_dfs

    self.single_table = single_table
    self.tc_left_join = tc_left_join
    self.tc_right_join = tc_right_join

    # Internals
    self.df_merged = None
    self._grouped = None
    self.df_subset_cache = {}


  # Create a merged table that only contains:
  #   the index of each seed table
  #   the column to merge by for each table
  #
  # column_seeds are the join criteria, e.g.
  # join users.zipcodeA == zipcodes.zipcodeB
  # Usually those are the same id, but not always.
  def merge_tables(self):
    table_left = self.tc_left_join.table
    table_right = self.tc_right_join.table
    self.df_left = self.get_working_df(table_left)
    self.df_right = self.get_working_df(table_right)

    # The extra [] means we'll the result as a DataFrame, not a Series.
    # Note: using .copy to get around potential undefined behavior.
    # See http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
    df_left_thin = self.df_left[ [self.tc_left_join.column] ].copy()
    df_left_thin[f'_index_{table_left}'] = df_left_thin.index

    df_right_thin = self.df_right[ [self.tc_right_join.column] ].copy()
    df_right_thin[f'_index_{table_right}'] = df_right_thin.index


    self.df_merged = pd.merge(
      left=df_left_thin,
      right=df_right_thin,
      left_on=self.tc_left_join.column,
      right_on=self.tc_right_join.column,
      sort=False,
      indicator=True,
    )

  def apply_crosstable_wheres(self, wcs):
    for wc in wcs:
      self.apply_crosstable_where(wc)

  # Return the merged-subset of data from each joined table, specified by the indexes in the merged dataframe.
  # Algorithm:
  # Determine tables to use
  # For each side:
  #   Take the indexes from that side of the merged dataframe (e.g. from _index_users or from _index_orders)
  #   Use those indexes to build a temporary dataframe
  # Use the comparison function on the left and right dataframes
  # Apply the mask to the merged dataframe
  def apply_crosstable_where(self, wc):
    self.log_df_merged(f'before {wc}')

    # wc.left / wc.right are tablecolumns.
    col_left = self.get_joined_subset_col(wc.left)
    col_right = self.get_joined_subset_col(wc.right)

    # Mask the rows and update the working merged table.
    mask_keep = apply_comparison_op(wc.comparisonOp, col_left, col_right)
    self.df_merged = self.df_merged[mask_keep.values]
    self.log_df_merged(f'after {wc}')


  def get_col(self, tc):
    if self.single_table:
      return self.get_working_df(tc.table)[tc.column]
    else:
      return self.get_joined_subset_col(tc)


  # The merged table is a filtered set of row indices that correspond to the table joins.
  # Each set of indexes can be used to get data from the underlying full source tables at this tstate.
  # This function takes the filtered, merged indices for a specific table, gets those rows from the source,
  # then returns a specific column from those rows.
  def get_joined_subset_col(self, tc):
    # Get the indexes
    indexes = self.df_merged[f'_index_{tc.table}']

    # Build the temporary dataframe from those indexes.
    # There may be duplication of indexes, which is normal.
    df = self.get_working_df(tc.table)

    # Get the data from the source table
    col_subset = df[tc.column][indexes]

    # Update the index to match the merged dataframe.
    # Note: this works fine for inner joins, but won't work for outer joins
    # since the left/right values can differ (the left join id could be NA where the right join id is populated)
    # Also todo: check what happens for NA values in the index.
    col_subset.index = self.df_merged[self.tc_left_join.column]
    return col_subset


  # The group has a list of where-filtered entries.
  # Return the subset of values for a particular table.
  def get_tc_subset_by_group(self, tc, group):
    indexes = group[f'_index_{tc.table}']
    df = self.working_dfs[tc.table]
    return df.loc[indexes][tc.column]


  # Returns the data associated with a particular tablecolumn for the specified group.
  def iterate_groups_by_tablecolumn(self, tc):
    # if self.single_table:
    #   df = self.working_dfs[self.single_table]
    #   for row in df.itertuples():
    #     yield getattr(row, 'index'), WrappedEntry(row=row)
    # else:

    for index, group in self.grouped:
      col = self.get_tc_subset_by_group(tc, group)
      yield index, col


  # You can output the groups as follows:
  # for label, group in self.grouped:
  #   print(str(label) + ':')
  #   print(group)
  def create_groups(self):
    self._grouped = self.df_merged.groupby(self.tc_left_join.column)


  @property
  def grouped(self):
    if not self._grouped:
      self.create_groups()

    return self._grouped


  def get_working_df(self, table):
    df = self.working_dfs.get(table)

    if df is None:
      raise Exception(f'Table {table} not found in the current dataset')

    return df


  def log_df_merged(self, msg):
    log.debug(f'Merged {msg}:\n{self.df_merged}')


  def get_join_tcs(self):
    return self.tc_left_join, self.tc_right_join


  def get_index(self):
    if self.single_table:
      return self.get_singletable_index()
    else:
      return self.get_grouped_index()

  # Note: this returns the FILTERED grouped index.
  def get_grouped_index(self):
    data = self.grouped.groups.keys()
    return pd.Index(data)

  # Note: this returns the FILTERED singletable index.
  def get_singletable_index(self):
    return self.get_working_df(self.single_table).index


  def get_num_cols(self):
    if self.single_table:
      return self.get_working_df(self.single_table).shape[0]
    else:
      return len(self.grouped)


  # Construct a dataframe from the results of a given table.
  # The table could have been filtered from where clauses.
  # If there's a join, the table will be constructed from the existing groups.
  # Also, cache the results of this query.
  def get_df_by_tablename(self, table):
    if self.single_table:
      return self.get_working_df(table)

    # Look up the cache
    df = self.df_subset_cache.get(table)
    if df is not None:
      return df

    unique_indexes = self.get_unique_indexes(table)
    if self.tc_left_join.table == table:
      df = self.get_working_df(self.tc_left_join.table)
    elif self.tc_right_join.table == table:
      df = self.get_working_df(self.tc_right_join.table)
    else:
      raise Exception('VirtualTable: table={table} not recognized; left={tc_left.table}, right={tc_right.table}')

    # Then cache and return a subset of the main table.
    self.df_subset_cache[table] = df.loc[unique_indexes]
    return self.df_subset_cache[table]


  def get_unique_indexes(self, table):
    # Cache miss - set the cache and return the value
    col = self.df_merged[f'_index_{table}']
    self.df_subset_cache[table] = pd.Series.unique(col)
    return self.df_subset_cache[table]


  def __str__(self):
    if self.single_table:
      return f'table={self.single_table}'
    else:
      return f'{self.tc_left_join.table}.{self.tc_left_join.column} == {self.tc_right_join.table}.{self.tc_right_join.column}'

  def __repr__(self):
    return f'<{type(self).__name__}: {str(self)}>'
