import collections
import pandas as pd
import numpy as np


ColTuple = collections.namedtuple('ColTuple', 'name, col')

class TransformResult():
  def __init__(self, *args, **kwargs):
    # Working dataset and original
    self.df = None
    self.df_orig = None

    # Masks
    self.df_mask_invalids = None
    self.df_mask_drops = None

    # Data to change
    self.newcoltuples = []
    self.set_drop_idxs = set()
    self.set_drop_cols = set()

    self.set_source_cols = set()
    self.set_dest_cols = set()
    self.table = None

  # This can't be done in the init because we don't have the data or its shape until execution time.
  def setup_data(self, df):
    self.df_orig = df
    self.df = df.copy(deep=True) if df is not None else None

    # Boolean dataframes
    self.df_mask_drops = pd.DataFrame(False, index=np.arange(df.shape[0]), columns=self.df_orig.columns)
    self.df_mask_invalids = pd.DataFrame(False, index=np.arange(df.shape[0]), columns=self.df_orig.columns)


  @property
  def list_drop_idxs(self):
    _list = list(self.set_drop_idxs)
    return sorted(_list)

  @property
  def list_drop_cols(self):
    _list = list(self.set_drop_cols)
    return sorted(_list)

  # This has to use df_orig for the col indexes to make sense.
  @property
  def list_drop_col_names(self):
    col_idxs = self.list_drop_cols
    return self.df_orig.columns[col_idxs].tolist()


  def get_new_colnames(self):
    return [coltuple.name for coltuple in self.newcoltuples]


  def add_new_col(self, name, vals, dtype):
    col = pd.Series(vals, dtype=dtype)
    coltuple = ColTuple(name=name, col=col)
    self.newcoltuples.append(coltuple)
    self.set_dest_cols.add(name)


  # Cols can be a single column or a list-like.
  def add_col_drops(self, colnames):
    col_idxs = [self.df.columns.get_loc(name) for name in colnames]
    self.set_drop_cols |= set(col_idxs)

  def remove_col_drop(self, colname):
    col_idx = self.df.columns.get_loc(colname)
    self.set_drop_cols.remove(col_idx)

  def __str__(self):
    return f'<{type(self).__name__}, newcols={self.get_new_colnames()}, list_drop_cols={self.list_drop_cols}, list_drop_idxs={self.list_drop_idxs}>'

  __repr__ = __str__
