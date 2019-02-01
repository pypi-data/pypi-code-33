import operator, pyparsing
import pandas as pd

from .set_functions import get_func_by_name
from .ops import apply_math_op
from .tablecolumn import TableColumn
from datamode.utils.data import is_basic_type
# from datamode.utils.perf import do_profile, profiler_singleton

from datamode.utils.utils import get_logger
log = get_logger(__name__)


class LinearExecutionManager():
  def __init__(self, timer=None, *args, **kwargs):
    self.timer = timer


  def execute_linear_plan_vectors(self, linear_plan, vt):
    arguments = []

    # breakpoint()
    for node in linear_plan:
      if node.type == 'tableColumn':
        # Gets the data at a particular table.column from the dataset. Can be a scalar or a list.
        # node.value is a table_column
        # arg can be either a pd.Series if there are no groupby clauses
        # or arg can be a set if there are groupby clauses.
        newarg = node.value
      elif node.type == 'operator':
        # Args can be raw pandas Series.
        # They can also just be tablecolumns, in which case we'll look up the appropriate values.
        arg2 = arguments.pop()
        arg1 = arguments.pop()

        if isinstance(arg1, TableColumn):
          col1 = vt.get_col(arg1)
        else:
          col1 = arg1

        if isinstance(arg2, TableColumn):
          col2 = vt.get_col(arg2)
        else:
          col2 = arg2

        # node.value is a string operator, e.g. '+'
        # arg1, arg2 are Series
        newarg = apply_math_op(node.value, col1, col2)

      elif node.type == 'func':
        # For now, we only support functions that operate on the set which results from a joined table.
        # That means it needs groups, and thus any single-table vt should raise an exception.
        if vt.single_table:
          raise Exception('LinearExecution: attempting to call aggregation function without join specified.')

        tc = arguments.pop()

        # With functions, we're aggregating a set of rows into a set of scalars,
        # which will then be used in the next operation.
        # In this case, we need to get the grouped set and operate on each member individually.
        if not isinstance(tc, TableColumn):
          raise Exception('LinearExecutionManager: Not yet implemented')

        data = []
        indexes = []
        for index, col in vt.iterate_groups_by_tablecolumn(tc):
          # breakpoint()
          val = node.func_fn(col)
          data.append(val)
          indexes.append(index)

        newcol = pd.Series(data, indexes)
        newarg = newcol

      elif node.type == 'primitive':
        # In apply_math_op, a pandas Series can perform a math operation directly with a scalar,
        # e.g. mycol + 5
        newarg = node.value

      arguments.append(newarg)

    # This is the last vector remaining. Expand it in case we get an interim value
    # like a tablecolumn or a primitive, e.g. 'total = 5', 'total = foo.abc'.
    return self.expand_final_result(vt, arguments[0])

    self.timer.report('Finished executing linear plan vectors') if self.timer else None



  # Since we're forced to lazy-load tablecolumns (because we don't know whether we need to group them or not),
  # we have to resolve the lazy-load if the expression is just a copied tablecolumn, e.g. 'foo.abc = foo.def'
  def expand_final_result(self, vt, result):
    if isinstance(result, TableColumn):
      return vt.get_col(result)

    # If we have a basic type, it's a single-table vt.
    # We have to use the index of the working table so that it will get properly set
    # in build_dest_col.
    if is_basic_type(result):
      index = vt.get_index()
      return pd.Series(result, index)

    if not isinstance(result, pd.Series):
      raise Exception('LinearExecutionManager: expected pandas.Series')

    # If we got here, we can just return the result as-is since it's a Series.
    return result

