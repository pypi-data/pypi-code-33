import math, datetime
import pytz, dateutil.parser
import json

import numpy as np
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_datetime64_any_dtype

from .core.transform_core import Transform
from .core.transform_result import TransformResult
from .columnartransform import ColumnarTransform
from .twocoltransform import TwoColTransform
from datamode.utils.data import is_val_none_equivalent

# ISOFORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'

from datamode.utils.utils import get_logger
log = get_logger(__name__)


class BlanksToNones(ColumnarTransform):
  def validate_column(self, col):
    return is_string_dtype(col)

  def transform_values(self, context, index, *args):
    val = args[0]
    if type(val) == str and val.strip() == '':
      return None
    return val


  def add_column_drops(self):
    colnames = self.get_colnames()
    self.result.add_col_drops(colnames)


# DropColumns and SelectColumns are just inverts of each other
class DropColumns(ColumnarTransform):
  def add_column_drops(self):
    cols_to_drop = self.get_colnames()
    self.result.add_col_drops(cols_to_drop)

  def do_process_table(self):
    return False


class SelectColumns(ColumnarTransform):
  def add_column_drops(self):
    cols_existing = self.result.df.columns
    cols_to_keep = self.get_colnames()
    cols_to_drop = [name for name in cols_existing if name not in cols_to_keep]

    self.result.add_col_drops(cols_to_drop)

  def do_process_table(self):
    return False


class StringToNumber(ColumnarTransform):
  def validate_column(self, col):
    return is_string_dtype(col)

  def transform_values(self, context, index, *args):
    val = args[0]
    return float(val)


parserinfo = dateutil.parser.parserinfo()

class CanonicalizeDate(ColumnarTransform):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.new_dtype = 'datetime64[ns]'

  def add_column_drops(self):
    cols_to_drop = self.get_colnames()
    self.result.add_col_drops(cols_to_drop)

  def validate_column(self, col):
    if is_string_dtype(col) or is_numeric_dtype(col):
      return True
    else:
      return False

  def transform_values(self, context, index, *args):
    val = args[0]

    # If it's None or equivalent, convert to None.
    if is_val_none_equivalent(val):
      return None

    if isinstance(val, int):
      if val > 1000000000000: # 1,000,000,000,000 probably in ms
        val = val / 1000
      try:
        dt = datetime.datetime.utcfromtimestamp(val)
      except:
        dt = val
    else:
      # If the val is a relative marker like 'January', 'Tuesday', leave it alone.
      if self.is_relative_marker(val):
        return val

      fmt = self.options.get('format')

      if fmt:
        dt = datetime.datetime.strptime(val, fmt)
      else:
        # Get both 30/3 and 3/30 dates
        try:
          dt = dateutil.parser.parse(val)
        except ValueError:
          dt = dateutil.parser.parse(val, dayfirst=True)

    return dt
    # return dt.strftime(CanonicalizeDate.ISOFORMAT)


  def is_relative_marker(self, val):
    if parserinfo.weekday(val) is not None or parserinfo.month(val) is not None:
      return True

    return False


class DropNumericalOutliers(ColumnarTransform):
  DROP_THRESHOLD_MULT_DEFAULT = 4

  def build_column_context(self, col):
    drop_threshold_mult = self.options.get('drop_threshold_mult', DropNumericalOutliers.DROP_THRESHOLD_MULT_DEFAULT)

    std = col.std()
    mean = col.mean()

    half_window = std * drop_threshold_mult

    context = {
      'std': std,
      'mean': mean,
      'drop_threshold_mult': drop_threshold_mult,
      'drop_max': mean + half_window,
      'drop_min': mean - half_window,
    }

    log.debug(f'DropNumericalOutliers context: {context}')
    return context

  def is_context_valid(self, context):
    if context['drop_threshold_mult'] == 0:
      return False

    return True

  def validate_column(self, col):
    return is_numeric_dtype(col)

  def transform_values(self, context, index, *args):
    val = args[0]
    if val > context['drop_max'] or val < context['drop_min']:
      self.result.set_drop_idxs.add(index)
      # We can't return None since pandas won't allow us to add None to a numerical dtype.
      # However, the row will be deleted so it won't matter anyway.
      return val

    return val

  def get_stats_str(self, context):
    return f'std={context["std"]:.2f}, drop_threshold= +-{context["drop_threshold"]:.2f}'


class ProcessNones(ColumnarTransform):

  def transform_values(self, context, index, *args):
    val = args[0]

    if is_val_none_equivalent(val):
      # log.debug(f'ProcessNones val={val} is None equivalent ')
      return self.perform_action(index, val)

    # log.debug(f'ProcessNones val={val} is not None equivalent ')
    return val

  # Defaults to dropping the row.
  def perform_action(self, index, val):
    action = self.options.get('action', 'drop')
    if action == 'zero':
      return 0
    if action == 'drop':
      # log.debug(f'Adding drop_idx={index}, val={val}.')
      self.result.set_drop_idxs.add(index)
      return None



class CombineDateAndTimeFragments(TwoColTransform):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.col_date = None
    self.col_time = None

  def set_new_dtype(self):
    self.new_dtype = 'datetime64[ns]'

  def get_colnames(self):
    return self.options['col_date'], self.options['col_time']


  def add_column_drops(self):
    if self.options['consume_originals']:
      colnames = self.get_colnames()

      colindex1 = self.result.df.columns.get_loc(colnames[0])
      colindex2 = self.result.df.columns.get_loc(colnames[1])

      self.result.set_drop_cols.add(colindex1)
      self.result.set_drop_cols.add(colindex2)


  def transform_values(self, context, index, *args):
    val1, val2 = args

    # pylint: disable=unused-variable
    dt, td = self.ensure_dts(val1, val2)
    return dt + td

  def ensure_dts(self, date, time):
    # Date
    if type(date) == str:
      dt = dateutil.parser.parse(date)
    else:
      dt = date

    # Time
    if type(time) == str:
      td = pd.to_timedelta(time)
    else:
      td = time

    return dt, td

  # If the date is valid, use it; otherwise return None.
  # Ignore the time value.
  def get_invalid_replacement(self, *args):
    date, dummy = args

    dt = None
    try:
      dt = dateutil.parser.parse(date)
    except Exception:
      pass

    if dt is None:
      return None

    return dt


  def validate_columns(self, col1, col2):
    date_valid = self.is_single_col_valid(col1)
    time_valid = self.is_single_col_valid(col2)
    return date_valid and time_valid

  def is_single_col_valid(self, col):
    if is_string_dtype(col):
      return True

    return is_datetime64_any_dtype(col)


# Example custom transform
# Inherit from Transform and override execute
# Or, inherit off any of the other base transform classes e.g. ColumnarTransform
class MyCustomTransform(Transform):
  def __init__(self, my_message, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.options['my_message'] = my_message

  def execute(self, tcon):
    log.info(self.options['my_message'])
    return TransformResult()


class NormalizeJson(ColumnarTransform):

  def transform_values(self, context, index, *args):
    val = args[0]

    try:
      val = json.loads(val)
      if not isinstance(val, dict):
        val = {}
    except:
      val = {}

    return val

  def process_single_column(self, col, colname):

    context = self.build_column_context(col)
    if not self.is_context_valid(context):
      log.debug(f'Context not valid, transform={self}, context={context}, colname={colname}')
      return None

    new_cols = {}
    none_array = []
    for index, oldval in col.iteritems():
      val = None

      try:
        val = self.transform_values(context, index, oldval)
        for k,v in new_cols.items():
          if k in val:
            new_cols[k].append(val[k])
            val.pop(k)
          else:
            new_cols[k].append(None)
        for k,v in val.items():
          insert_array = none_array.copy()
          insert_array.append(v)
          new_cols[k] = insert_array

      except (ValueError, TypeError):
        val = self.handle_invalid(context, index, oldval)

      none_array.append(None)

    new_col_prefix = colname + '.'
    for k, v in new_cols.items():
      new_col_name = new_col_prefix + k
      self.result.add_new_col(new_col_name, v, None)


class DropDuplicates(ColumnarTransform):

  def build_column_context(self, col):
    context = {
      'incoming_val': None,
      'previous_val': None,
    }

    return context

  def setup_data(self, df):
    self.result.setup_data(df)

    # data needs to be sorted to iterate through rows
    # and identify/drop duplicates
    self.result.df.sort_values([self.options['cols']],
      ascending=self.options.get('ascending', True),
      inplace=True
    )

  def transform_values(self, context, index, *args):
    val = args[0]
    if self.options.get('ignore_nones', False) and not val:
      pass
    else:
      context['incoming_val'] = val
      if context['incoming_val'] == context['previous_val']:
        self.result.set_drop_idxs.add(index)
        return None

      context['previous_val'] = val

    return val

  def process_dataframe_changes(self):
    self.drop_rows()

  def execute(self, tcon):
    # a clone of the parent's execute
    # but references this classes' setup_data
    # with sorting func
    self.setup_data(tcon.df_current)

    self.add_column_drops()
    self.set_new_dtype()

    if self.do_process_table():
      self.process_table()

    self.process_result()

    return self.result


# merged_table: the name to use for the merged table.
# tables: a list of already-loaded tables to use.
# relations: how to connect the tables together.
class CombineTables(Transform):
  def __init__(self, merged_table, tables, relations, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.options['merged_table'] = merged_table
    self.options['tables'] = tables
    self.options['relations'] = relations

  def execute(self, tcon):
    table0, table1 = self.options['tables'][0], self.options['tables'][1]
    relation = self.options['relations'][0]

    df0 = tcon.ds.tstate_last.get_df(table0)
    df1 = tcon.ds.tstate_last.get_df(table1)

    self.result.df = pd.merge(
      left=df0, right=df1,
      on=relation,
      #  left_on=None, right_on=None,
      sort=False,
      # suffixes=('_' + self.options['tables'][0], '_' + self.options['tables'][1]),
      indicator=True,
      #   validate='one_to_one'
    )

    tcon.current_table = self.options['merged_table']
    log.info(f'Created merged table {tcon.current_table}')

    return self.result

