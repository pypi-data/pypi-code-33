import abc
from .transform_result import TransformResult

from datamode.utils.utils import get_logger
log = get_logger(__name__)


class Transform(abc.ABC):

  def __init__(self, *args, **kwargs):
    self.options = kwargs.copy()
    self.result = TransformResult()
    self.new_dtype = None

    # Can be overridden
    self.keep_original_columns = False


  def execute(self, tcon):
    self.result.setup_data(tcon.df_current)

    self.add_column_drops()
    self.set_new_dtype()

    # Some transforms don't need to process row-by-row.
    if self.do_process_table():
      self.process_table()

    self.process_result()

    return self.result


  def process_result(self):
    self.process_dataframe_changes()


  def drop_rows(self):
    drop_idxs = self.result.list_drop_idxs  # Computed, so could be expensive
    # log.debug(f'Dropping rows: {drop_idxs}')

    if not drop_idxs:
      return

    self.result.df.drop(drop_idxs, inplace=True)
    self.result.df.reset_index(drop=True, inplace=True)


  # Drop columns first, then rows.
  def process_dataframe_changes(self):
    drop_col_idxs = self.result.list_drop_cols
    coltuples = self.result.newcoltuples

    newcolnames = self.result.get_new_colnames()

    # log.debug(f'Drop columns: {drop_col_idxs}, replacements={newcolnames}')

    # Split into replacement and straight add/drop lists
    drop_cols_idxs_replace, coltuples_replace, drop_cols_idxs_simple, coltuples_simple = get_list_remainders(drop_col_idxs, coltuples)
    # log.debug(f'{drop_cols_idxs_replace}, {coltuples_replace}, {drop_cols_idxs_simple}, {coltuples_simple}')

    # If we have any matching drop/additions, perform the replacements.
    for drop_col_idx, coltuple in zip(drop_cols_idxs_replace, coltuples_replace):
      col = coltuple.col if coltuple else None
      name = coltuple.name if coltuple else None
      self.result.df = replace_dataframe_column(self.result.df, drop_col_idx, col, name)


    # Now drop any remaining drop columns (reverse order)
    drop_col_names_simple = [self.result.df.columns[idx] for idx in drop_cols_idxs_simple]
    if drop_col_names_simple:
      self.result.df.drop(drop_col_names_simple, axis='columns', inplace=True)

    # Then add any remaining new columns
    for coltuple in coltuples_simple:
      self.result.df[coltuple.name] = coltuple.col

    # After the above, dropping rows should be simple :)
    self.drop_rows()

    log.info(f'''Changes:   {type(self).__name__}
\tNew cols:\t{newcolnames}\n\tDropped cols:\t{self.result.list_drop_col_names}
\tDropped_rows:\t{len(self.result.list_drop_idxs)}.
\tColumns:\t{self.result.df.shape[1]}
\tRows:\t\t{self.result.df.shape[0]}''')


  def get_invalid_replacement(*args):
    return None

  def transform_values(self, context, index, *args):
    return args[0]

  def add_column_drops(self):
    pass

  def set_new_dtype(self):
    pass

  def process_table(self):
    pass

  def do_process_table(self):
    return True

  def __str__(self):
    return f'{type(self).__name__}, options={str(self.options)}'

  __repr__ = __str__



# Drops a single column and replaces it with the new column.
def replace_dataframe_column(df, drop_col_idx, newcol, newcol_name):
  # log.debug(f'Dropping column {drop_col_idx}: {df.columns[drop_col_idx]}')
  drop_col_name = df.columns[drop_col_idx]
  df.drop(drop_col_name, axis='columns', inplace=True)

  # log.debug(f'Inserting {newcol_name} at index {drop_col_idx}')
  df.insert(drop_col_idx, newcol_name, newcol)

  return df



# Given two lists, return two lists with the shared minimum length, then return two lists with the remainder
# E.g. given [1, 2, 3] and [a, b, c, d, e, f]:
# this will return [1, 2, 3], [a, b, c], [], [d, e, f]
def get_list_remainders(a, b):
  num_a = len(a)
  num_b = len(b)
  num_min = min(num_a, num_b)

  return a[:num_min], b[:num_min], a[num_min:], b[num_min:]


# Todo: this doesn't really work for strings
# Todo: also, need to dedupe columns if one appears multiple times
# Select columns based on Pandas dtype
def expand_dtype_columns(df, cols):
  cols_output = []

  # This supports multiple column dtypes like ['@object', '@number']
  for col in cols:
    if col in ['@object', '@number', '@datetime', '@bool']:
      dtype = col[1:]
      cols_by_dtype = df.select_dtypes(dtype).columns
      log.debug(f'Cols for dtype matching {dtype}: {cols}')
      cols_output += list(cols_by_dtype)
    else:
      cols_output += [col]

  # Remove dupes, if any
  cols_output_clean = []
  # cols_output = list(set(cols_output))
  for i in cols_output:
    if i not in cols_output_clean:
      cols_output_clean.append(i)

  return cols_output_clean
