import pyparsing, pprint
import pandas as pd
import numpy as np
from collections import namedtuple
from pandas.api.types import is_numeric_dtype, is_bool_dtype, is_object_dtype, is_datetime64_any_dtype, is_timedelta64_dtype

from ..transforms import Transform
from .parser import baseExpr
from .tablecolumn import TableColumnManager, TableColumn
from .execution_manager import ExecutionManager
from datamode.utils.timer import CustomTimer
from datamode.utils.utils import DONT_YOU_WANT_TO_EXPRESS_YOURSELF

from datamode.utils.utils import get_logger
log = get_logger(__name__)


WhereClause = namedtuple('WhereClause', 'left right comparisonOp')
JoinClause = namedtuple('JoinClause', 'left right')


# And not the lawyerly kind.
class Action():
  def __init__(self, _type, dest, infix, default=None, drop_target_table=None, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.type = _type
    self.dest = dest
    self.infix = infix
    self.default = default

    self.drop_target_table = drop_target_table
    self.tc_dest = None
    self.head = None
    self.linear_plan = None
    return

  def __str__(self):
    return f'type={self.type}, dest={self.dest} infix={self.infix}'

  def __repr__(self):
    return f'<{type(self).__name__}: {str(self)}>'



def drop_duplicate_indexes(col):
  return col[ ~col.index.duplicated(keep='first') ]


COMPARISON_OPERATOR_REVERSE_MAP = {
  '<': '>',
  '<=': '>=',
  '==': '==',
  '!=': '!=',
  '>=': '<=',
  '>': '<',
}


class Expression(Transform):
  def __init__(self, expression, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.options['expression'] = expression
    self.parse_results = None

    # Main working datastore by table name.
    self.working_dfs = {}
    self.timer = None


  def execute(self, tcon):
    # Uncomment to get detailed timing logs
    # self.timer = CustomTimer(log, 'Expression')

    # These can't be initialized in the constructor, since we don't have tcon till now.
    self.tcon = tcon
    # todo: the copy might not be necessary.
    self.working_dfs = self.tcon.ds.tstate_last.dfs.copy()  # Shallow copy
    self.tcm = TableColumnManager(self.tcon.current_table, self.working_dfs)

    if self.options['expression'].strip() == '':
      raise Exception(DONT_YOU_WANT_TO_EXPRESS_YOURSELF)

    try:
      self.report('Starting parse')
      self.parse_results = baseExpr.parseString(self.options['expression'])
    except pyparsing.ParseException:
      raise Exception('There was a problem parsing your expression.')

    self.report('Finished parsing')

    # Single-table wheres
    where_clauses = self.process_wheres()
    # log.debug('\n' + pprint.pformat(where_clauses))

    join_clauses = self.process_joins()
    # log.debug('\n' + pprint.pformat(join_clauses))

    actions = self.process_actions()
    # log.debug('\n' + pprint.pformat(actions))

    groupbys = self.process_groupbys()
    # log.debug('Groupbys:\n' + pprint.pformat(groupbys))

    self.report('Processed all directives')

    em = ExecutionManager(self.working_dfs, self.tcon.current_table, self.tcm, timer=self.timer)
    self.report('Created ExecutionManager')

    em.build_action_trees(actions)

    em.build_virtual_table(where_clauses, join_clauses)
    self.report('Built virtual table')

    self.apply_actions(em, actions)
    self.report('Applied all actions')

    return self.result

  def report(self, msg):
    if self.timer:
      self.timer.report(msg)


  def apply_actions(self, em, actions):
    for action in actions:
      if action.type == 'droprows':
        self.apply_action_droprows(em, action)
        self.report('Finished applying droprows')

      elif action.type == 'assignment':
        # Only assignments have full tablecolumns; drop only has a table.
        action.tc_dest = self.get_destination_tablecolumn(action.dest)
        self.apply_action_assignment(em, action)
        self.report('Finished action, dest={action.tc_dest}, infix={action.infix}')
      else:
        raise Exception(f'Expression: action.type={action.type} not known')


  # Drop rows must specify a single table to drop from.
  #
  # Note that even though only one table can have dropped rows,
  # it can still be joined to other tables to inform the drop, eg:
  #   drop rows from users
  #   where orders.price > 5000
  #   join users.user_id = orders.user_id
  def apply_action_droprows(self, em, action):
    # This is the original dataframe.
    df = self.tcon.ds.tstate_last.get_df(action.drop_target_table)
    self.result.setup_data(df)

    # This is the filtered dataframe.
    df_target = em.get_df_by_tablename(action.drop_target_table)

    for index in df_target.index.values:
      self.result.set_drop_idxs.add(index)

    self.result.table = action.drop_target_table
    self.process_result()


  def apply_action_assignment(self, em, action):
    # Get the source df for reference.
    df = self.tcon.ds.tstate_last.get_df(action.tc_dest.table)
    self.result.setup_data(df)

    # Calculate the values.
    vals = em.apply_action_assignment(action)
    self.report('Finished building vals')

    # Build the new column from those new values.
    join_id = self.get_join_column(em, action.tc_dest)
    dtype = self.determine_dtype(vals)
    destcol = self.build_dest_col(action.tc_dest, join_id, vals, action.default, dtype)

    # Write the changes back to the dataframe.
    # Note: if there's a new table, we'll have to add a new dataframe here.
    self.result.table = action.tc_dest.table
    self.result.add_new_col(action.tc_dest.column, destcol.values, dtype)
    self.process_result()
    self.report('Finished processing result')


  # Todo: make this more robust
  # Notes:
  #   Currently you can't mix string and int types, even when using 'object' dtype,
  #   because pyarrow chokes on that.
  def determine_dtype(self, vals):
    if len(vals) == 0:
      return np.float64

    # Lazy tuple iteration, although we just need the first one
    for index, val in vals.iteritems():
      if val is None:
        continue

      _type = type(vals.iloc[0])

      if _type == str:
        return 'object'
      # Amazingly, np.bool also returns true for is_numeric_dtype, so this should come before numeric.
      elif is_bool_dtype(_type):
        return np.bool
      elif is_datetime64_any_dtype(_type):
        return 'datetime64[ns]'
      elif is_timedelta64_dtype(_type):
        return 'timedelta64[ns]'
      elif is_numeric_dtype(_type):
        return np.float64
      elif is_object_dtype(_type):
        return 'object'

      raise Exception('Expression: type {_type} not supported yet')

    # All vals were None, so use 'object'.
    return 'object'

  def get_join_column(self, em, tc_dest):
    tc_join_left, tc_join_right = em.get_join_tcs()
    if not tc_join_left or not tc_join_right:
      return None

    if tc_dest.table == tc_join_left.table:
      return tc_join_left.column
    elif tc_dest.table == tc_join_right.table:
      return tc_join_right.column
    else:
      raise Exception('Expression: joins specified but table not present')


  def build_dest_col(self, tc_dest, join_id, vals, default, dtype):
    df_orig = self.tcon.ds.tstate_last.get_df(tc_dest.table)

    if join_id is None:
      return self.build_dest_col_by_singletable(df_orig, tc_dest, vals, default, dtype)
    else:
      return self.build_dest_col_by_group_index(df_orig, tc_dest, join_id, vals, default, dtype)


  # If we have a single table, the destination column will already have the same indexes as valscol.
  # However, because some df_orig rows could have been filtered by single-table where clauses,
  # they aren't guaranteed to be the same size. That's not a problem because Pandas will just put nulls
  # in any place where it can't match up indexes.
  def build_dest_col_by_singletable(self, df_orig, tc_dest, valscol, default, dtype):
    destcol = pd.Series(default, df_orig.index, dtype=dtype)
    destcol[valscol.index] = valscol
    return destcol


  # The return value of action assignments doesn't always return a Series of the same size.
  # The destination table might have duplicate rows, e.g.:
  # userid1 and userid2 might have the same zipcode and want zipcode_income to be the same
  #
  # Or a row might not have a corresponding index at all, because it was filtered out, e.g.:
  # userid1 might have a corresponding value for zipcode_income, but userid3 might have nothing.
  #
  # So we iterate over the grouped result set and fill in any matching entries that correspond
  # to the destination table.
  def build_dest_col_by_group_index(self, df_orig, tc_dest, join_id, valscol, default, dtype):

    # We need to get the original destination df, not the working df which is filtered.
    destindex = df_orig[join_id]
    destcol = pd.Series(default, destindex.values, dtype=dtype)

    # Find out whether there are any indexes in valscol that aren't in destcol.
    # For example, users.foo = orders.bar + users.baz  -> if some users don't have orders,
    # there will be some NA values and so indexing can't be used for that destcol.
    extra_labels = valscol.index.difference(destcol.index)
    if len(extra_labels) > 0:
      valscol = valscol.drop(extra_labels)


    valscol = drop_duplicate_indexes(valscol)

    destcol.loc[valscol.index] = valscol
    destcol.index = df_orig.index
    return destcol


  def process_actions(self):
    actions = []

    # Get all the tables we care about and put them in a dict
    for _action in self.parse_results.actions:
      # droprows is handled inline for now
      if 'droprowsAction' in _action:
        action = Action('droprows', None, None, drop_target_table=_action.droprowsAction.table)
        actions.append(action)

      elif 'assignmentAction' in _action:
        assignmentAction = _action.assignmentAction
        # print(assignmentAction.dump())

        # Note that if the column exists, it will overwrite the existing column.
        # Otherwise, it will create a new column.
        action = Action('assignment', assignmentAction.destination, assignmentAction.infix)
        if assignmentAction.default:
          action.default = assignmentAction.default.primitive

        actions.append(action)


    return actions


  def process_groupbys(self):
    groupbys = []

    for groupby in self.parse_results.groupbysClause:
      tc = TableColumn(groupby.table, groupby.column)
      groupbys.append(tc)

    return groupbys


  def process_joins(self):
    join_clauses = []
    for join in self.parse_results.joinsClause:
      table = join.left.tableColumn.table
      column = join.left.tableColumn.column
      tc_left = TableColumn(table, column)

      table = join.right.tableColumn.table
      column = join.right.tableColumn.column
      tc_right = TableColumn(table, column)

      jc = JoinClause(tc_left, tc_right)
      join_clauses.append(jc)
    return join_clauses


  def get_destination_tablecolumn(self, destination):
    tc = self.tcm.get_destination_tablecolumn(destination)

    # We might have a specified table, but that table isn't guaranteed to exist yet.
    # If not, create it.
    table_exists = self.has_working_df(tc.table)
    if not table_exists:
      # This should also add it automatically to self.tcm.working_dfs.
      self.working_dfs[tc.table] = pd.DataFrame()
      self.tcon.current_table = tc.table
      log.debug(f'Created new table {tc.table}')

    return tc


  # Parser primitives:
  # whereStandard = whereLeft + comparisonOp + whereRight
  # whereIsNull = whereLeft + is_null
  # Note that the left clause always exists, but the right clause won't if it's null.
  def process_wheres(self):
    where_clauses = []

    for _where in self.parse_results.wheresClause:
      # Can be None
      primitive_left = _where.left.get('primitive')
      primitive_right = _where.right.get('primitive') if _where.right else None
      primitive_left_exists = primitive_left is not None
      primitive_right_exists = primitive_right is not None

      # Can only be on the right
      is_null = _where.get('is_null')

      # We can't have two primitives.
      if primitive_left_exists and primitive_right_exists:
        raise Exception('Expression: where clause is illegally comparing two primitive values.')

      tc_left = self.tcm.get_tablecolumn_from_raw_construct(_where.left, validate_column_exists=True)
      tc_right = self.tcm.get_tablecolumn_from_raw_construct(_where.right, validate_column_exists=True) if _where.right else None

      # If we have both, we have a dynamic where.
      if tc_left is not None and tc_right is not None:
        where_clauses.append(
          WhereClause(tc_left, tc_right, _where.comparisonOp)
        )

        continue

      # Special handling for the is_null case.
      if is_null:
        where_clauses.append(
          WhereClause(tc_left, None, 'isnull')
        )
        continue


      # We've already checked for two primitives and two non-primitives.
      # So the tablecolumn must be either on the left or the right.
      # Also, if the primitive is on the left, reverse the comparisonOp direction,
      # because the tablecolumn to primitive comparison is always calculated left-right.
      tc = tc_left or tc_right
      if tc_left is not None:
        tc = tc_left
        comparisonOp = _where.comparisonOp
      else:
        tc = tc_right
        comparisonOp = COMPARISON_OPERATOR_REVERSE_MAP[_where.comparisonOp]

      primitive = primitive_left or primitive_right

      # primitive and comparisonOp can be false if right_is_null is true.
      where_clauses.append(
        WhereClause(tc, primitive, comparisonOp)
      )

    return where_clauses


  def has_working_df(self, table):
    return table in self.working_dfs

  def get_working_df(self, table):
    df = self.working_dfs.get(table)

    if df is None:
      raise Exception(f'Table {table} not found in the current dataset')

    return df
