import re

from .core.transform_core import Transform, expand_dtype_columns
from .core.transform_result import TransformResult

from datamode.utils.utils import get_logger
log = get_logger(__name__)


class ColumnarTransform(Transform):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.options['cols'] = args[0]

    # Overridable
    # self.col = None
    self.new_dtype = None


  def process_table(self):
    # print(type(self).__name__)
    # import ipdb; ipdb.set_trace()

    colnames = self.get_colnames()

    for colname in colnames:
      col = self.result.df[colname]

      if not self.validate_column(col):
        log.warning(f'Column {colname} is invalid, passed in cols={self.options["cols"]}')
        # Remove it from any dropped columns because we don't want to touch it.
        self.result.remove_col_drop(colname)

        continue

      self.process_single_column(col, colname)

  def process_single_column(self, col, colname):
    # log.debug(f'Processing single column {colname}')

    context = self.build_column_context(col)
    if not self.is_context_valid(context):
      log.debug(f'Context not valid, transform={self}, context={context}, colname={colname}')
      return None

    colindex = self.result.df.columns.get_loc(colname)
    context['colindex'] = colindex

    vals = []
    for index, oldval in col.iteritems():
      val = None

      try:
        val = self.transform_values(context, index, oldval)
      except (ValueError, TypeError):
        val = self.handle_invalid(context, index, oldval)

      vals.append(val)

    dtype = None
    if self.new_dtype:
      dtype = self.new_dtype
    else:
      dtype = col.dtype

    self.result.add_new_col(colname, vals, dtype)


  def handle_invalid(self, context, index, *args):
    # result.invalid_idxs.append(index)
    oldval = args[0]
    return self.get_invalid_replacement(oldval)


  def get_colnames(self):
    cols = self.options['cols']

    # Regexes
    if type(cols) == str and self.options.get('cols_regex'):
      # https://stackoverflow.com/questions/3640359/regular-expressions-search-in-list
      regex = re.compile(cols, re.IGNORECASE)

      # Sometimes we get a 'quoted_string' sqlalchemy obj instead of strings.
      df_columns = [str(col) for col in self.result.df.columns.tolist()]
      cols = list(filter(regex.search, df_columns))
      return cols

    # Convert to array if it's a single string
    if type(cols) == str:
      cols = [cols]

    cols = expand_dtype_columns(self.result.df, cols)

    # Wildcards
    if cols == ['*']:
      cols = [str(col) for col in self.result.df.columns.tolist()]

    self.result.set_source_cols = set(cols)
    self.result.set_dest_cols = set(cols)

    return cols


  ###
  ### Overridable functions
  ###
  ### Note: These are not defined with @abc.abstractmethod because they don't have to be overridden, but can be.

  def build_column_context(self, col):
    return {}

  def validate_column(self, col):
    return True

  def is_context_valid(self, context):
    return True
