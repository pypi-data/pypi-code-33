import pprint
import pandas as pd

from .ops import apply_comparison_op
from .tablecolumn import TableColumn
from .virtualtable import VirtualTable
from .set_functions import get_func_by_name
from .expression_node import ExpressionNode
from .linear_execution import LinearExecutionManager

from datamode.utils.utils import get_logger
log = get_logger(__name__)


# from datamode.utils.perf import do_profile, profiler_singleton


class ExecutionManager():
  def __init__(self, dfs, tcon_current_table, tcm, timer=None, *args, **kwargs):
    self.working_dfs = dfs
    self.vt = None
    self.tcon_current_table = tcon_current_table
    self.tcm = tcm  # TableColumnManager
    self.lem = LinearExecutionManager()
    self.timer = timer


  def build_virtual_table(self, where_clauses, join_clauses):
    # breakpoint()

    where_clauses_crosstable = self.apply_wheres(where_clauses)
    self.report('Finished applying singletable wheres')

    if join_clauses:
      # For now, we only support one join.
      jc = join_clauses[0]

      # Create a merged table with just the ids and indexes of the left/right tables.
      self.vt = VirtualTable(self.working_dfs, tc_left_join=jc.left, tc_right_join=jc.right)
      self.report('Finished building VirtualTable')

      self.vt.merge_tables()
      self.report('Finished merging tc_left_join={jc.left}, tc_right_join={jc.right}')

      self.vt.apply_crosstable_wheres(where_clauses_crosstable)
      self.report('Finished applying crosstable wheres')

    else:
      if len(self.tcm.source_tables_seen) > 1:
        raise Exception('Expression: Multiple tables specified without a join.')

      # If there's no join, we expect to have a single source table.
      # The table should come from the source columns used in the query.
      table = next(iter(self.tcm.source_tables_seen))
      self.vt = VirtualTable(self.working_dfs, single_table=table)
      self.report('Finished building VirtualTable')


  # Returns a set of crosstable wheres (which require a virtual table merge to process)
  def apply_wheres(self, where_clauses):
    where_clauses_crosstable = []
    for wc in where_clauses:
      # Isnull?
      if wc.right == None and wc.comparisonOp == 'isnull':
        self.apply_where_isnull_filter(wc.left)
      # Both tables? Either single or crosstable.
      elif isinstance(wc.left, TableColumn) and isinstance(wc.right, TableColumn):
        if wc.left.table == wc.right.table:
          # Can use either table
          self.apply_singletable_where(wc.left, wc.left.column, wc.right.column, wc.comparisonOp)
        else:
          where_clauses_crosstable.append(wc)
      # One table, one primitive.
      else:
        self.apply_primitive_where(wc.left, wc.right, wc.comparisonOp)

    return where_clauses_crosstable


  # todo: support 'is not null'.
  def apply_where_isnull_filter(self, tc):
    df = self.get_working_df(tc.table)
    self.log_df(df, tc, 'before isnull')

    col = df[tc.column]

    mask_keep = col.isnull()
    df = df[mask_keep]
    self.working_dfs[tc.table] = df

    self.log_df(df, tc, 'after isnull')


  def apply_singletable_where(self, tc, col1, col2, comparisonOp):
    # tc_left and tc_right have the same table, so we can use either.
    df = self.get_working_df(tc.table)
    self.log_df(df, tc, f'before {col1} {comparisonOp} {col2}')

    mask_keep = apply_comparison_op(comparisonOp, df[col1], df[col2])
    df = df[mask_keep]
    self.working_dfs[tc.table] = df
    self.report(f'Applied singletable where: {col1} {comparisonOp} {col2}')
    self.log_df(df, tc, f'after {col1} {comparisonOp} {col2}')



  # @do_profile(profiler=profiler_singleton)
  def apply_primitive_where(self, tc, primitive, comparisonOp):
    df = self.get_working_df(tc.table)
    self.log_df(df, tc, f'before {tc} {comparisonOp} {primitive} ')

    mask_keep = apply_comparison_op(comparisonOp, df[tc.column], primitive)
    df = df[mask_keep]
    self.working_dfs[tc.table] = df
    self.report(f'Applied primitive where: {tc} {comparisonOp} {primitive}')
    self.log_df(df, tc, f'after {tc} {comparisonOp} {primitive} ')


  def get_working_df(self, table):
    df = self.working_dfs.get(table)

    if df is None:
      raise Exception(f'Table {table} not found in the current dataset')

    return df


  def build_action_trees(self, actions):
    actions_assignment = [action for action in actions if action.type == 'assignment']
    for action in actions_assignment:
      # Build the tree
      action.head = ExpressionNode(self.tcm, action.infix)
      self.report(f'Finished building tree for action={action}')

      # Traverse the tree to build the linear execution plan
      linear_plan = []

      # Closure
      def visit_fn(side, level, node, left, right):
        linear_plan.append(node)
        # whitespace = ' ' * level
        # log.debug(f'{whitespace}({level}{side}) Visited item={item}, type={node.type}, value={node.value}, left={left}, right={right}')

      # Actual tree traversal
      action.head.postorder_traversal(visit_fn)
      # log.debug(f'Execution plan:\n{pprint.pformat(linear_plan)}')

      self.report(f'Finished building linear execution plan for action={action}')
      action.linear_plan = linear_plan


  def apply_action_assignment(self, action):
    # Execute the plan, vectorized
    vals = self.lem.execute_linear_plan_vectors(action.linear_plan, self.vt)
    self.report('Finished executing linear plan')
    return vals

  def log_df(self, df, tc, msg):
    # log.debug(f'{tc.table}.{tc.column} {msg}:\n{df}')
    pass

  def report(self, msg):
    if self.timer:
      self.timer.report(msg)


  ###
  ### Passthrough functions to self.vt
  ###
  def get_join_tcs(self):
    return self.vt.get_join_tcs()

  def get_df_by_tablename(self, table):
    return self.vt.get_df_by_tablename(table)


  def __str__(self):
    return f'vt={self.vt}, tables={self.working_dfs.keys()} current_table={self.tcon_current_table}'

  def __repr__(self):
    return f'<{type(self).__name__}: {str(self)}>'
