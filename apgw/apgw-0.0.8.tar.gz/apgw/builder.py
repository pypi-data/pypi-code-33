'''Contains methods for building out SQL.'''
from typing import (Any, Mapping, Optional, List, Set, Tuple)
from apgw.constraint import (BinaryConstraint, Constraints, TextConstraint, Literal, DictConstraint)
from apgw.types import (SQL)
from apgw.util import (constraint_list_to_sql)
from apgw.types import (InsertAssignments, LimitOffset, Record)

def diff(source: Record, updates: Record, keys: Set[str] = None) -> Record:
  '''This returns the subset of :updates: that is different from :source: based on :keys:.

  :param source: the source item
  :param updates: the updates item
  :param keys: the subset of keys to check. If None, updates.keys() is used
  '''
  output = {}

  if keys is None:
    keys = set(updates.keys())

  for key in keys:
    if key not in source:
      raise Exception('Key {} not found in source object'.format(key))
    if key not in updates:
      raise Exception('Key {} not found in updates object'.format(key))
    if source[key] != updates[key]:
      output[key] = updates[key]

  return output

def build_constraint(data: Mapping[str, Any], cols: List[str]) -> DictConstraint:
  '''Builds a DictConstraint from a dict and a list of columns.'''
  return DictConstraint(((col, data[col]) for col in cols))

def constraints_to_sql(
    constraints: Optional[Constraints],
    *,
    paren: bool = True,
    joiner: str = ' and ',
    offset: int = 0,
    handle_null: bool = True) -> SQL:
  '''This methods converts a constraints object to SQL and params.

  :param constraints: the constraints to convert
  :param paren: if True, each constraint will be surrounded by parens
  :param joiner: how to join the constraint strings together
  :param offset: the offset to use for the constraint placeholders
  :param handle_null: if True, constraint values of None will be handled specially
  '''
  if constraints is None:
    return (None, [])

  if isinstance(constraints, TextConstraint):
    # Replaces all occurrences of '$0' with a numbered placeholder. This makes it so the calling
    # code doesn't have to know the exact numbers
    sql = constraints.sql
    placeholder = 1
    while sql.find('$0') != -1:
      sql = sql.replace('$0', '${}'.format(placeholder + offset), 1)
      placeholder += 1

    return (sql, constraints.params or [])

  if isinstance(constraints, DictConstraint):
    constraint_list = [BinaryConstraint(k, v) for k, v in constraints.items()]
  elif isinstance(constraints, list):
    constraint_list = constraints
  elif isinstance(constraints, BinaryConstraint):
    constraint_list = [constraints]
  else:
    raise Exception('Invalid constraint type')

  return constraint_list_to_sql(
      constraint_list,
      paren=paren,
      joiner=joiner,
      offset=offset,
      handle_null=handle_null
  )

def select_sql(
    table_name: str,
    constraints: Constraints = None,
    *,
    columns: str = '*',
    order_by: str = None,
    limit: LimitOffset = None
) -> SQL:
  '''Generates a select statement.

  :param table_name: the name of the table to select from
  :param constraints: the constraints for the select filter
  :param columns: the columns to select
  :param order_by: how to order the results
  :param limit: the limit and offset of the results
  '''
  (constraint_sql, params) = constraints_to_sql(constraints)

  sql = 'select {} from {}'.format(columns, table_name)

  if constraint_sql:
    sql = '{} where {}'.format(sql, constraint_sql)

  if order_by:
    sql = '{} order by {}'.format(sql, order_by)

  if limit:
    (limit_num, offset_num) = limit
    if limit_num:
      sql = '{} limit {}'.format(sql, limit_num)
    if offset_num:
      sql = '{} offset {}'.format(sql, offset_num)

  return (sql, params)

def insert_sql(
    table_name: str,
    assignments: InsertAssignments,
    *,
    returning: str = None) -> SQL:
  '''Generates an insert statement.

  :param table_name: the name of the table to insert on
  :param assignments: the insert assignments
  :param returning: a returning column list
  '''
  assign: List[Tuple[str, Any]]

  if isinstance(assignments, list):
    assign = assignments
  else:
    assign = [(k, v) for (k, v) in assignments.items()]

  columns = ', '.join(c for (c, _) in assign)
  placeholder_list = []
  params = []
  placeholder = 1

  for (_, val) in assign:
    if isinstance(val, Literal):
      placeholder_list.append(val.value)
    else:
      placeholder_list.append('${}'.format(placeholder))
      placeholder += 1
      params.append(val)
  placeholders = ', '.join(placeholder_list)

  sql = 'insert into {table_name} ({columns}) values ({placeholders})'.format(
      table_name=table_name,
      columns=columns,
      placeholders=placeholders)

  if returning:
    sql = '{} returning {}'.format(sql, returning)

  return (sql, params)

def update_sql(
    table_name: str,
    assignments: Constraints,
    constraints: Constraints = None,
    *,
    timestamp_col: str = 'updated_at',
    returning: str = None) -> SQL:
  '''Generates an update statement.

  :param table_name: the name of the table to update
  :param assignments: the updates to make
  :param constraints: the filter for the updates
  :param timestamp_col: the 'updated_at' column, if any
  :param returning: the list of colums to return from the update statement
  '''
  if timestamp_col and assignments:
    if isinstance(assignments, TextConstraint):
      raise Exception('Cannot combine timestamp_col and TextConstraint for update')
    elif isinstance(assignments, DictConstraint):
      assignments[timestamp_col] = Literal('now()')
    elif isinstance(assignments, BinaryConstraint):
      assignments = [assignments, BinaryConstraint(timestamp_col, Literal('now()'))]
    else:
      assignments.append(BinaryConstraint(timestamp_col, Literal('now()')))

  (assign_sql, assign_params) = constraints_to_sql(
      assignments,
      paren=False,
      joiner=', ',
      handle_null=False)
  (constraint_sql, constraint_params) = constraints_to_sql(
      constraints,
      paren=True,
      offset=len(assign_params))

  sql = 'update {} set {}'.format(table_name, assign_sql)

  if constraint_sql:
    sql = '{} where {}'.format(sql, constraint_sql)

  if returning:
    sql = '{} returning {}'.format(sql, returning)

  return (sql, assign_params + constraint_params)

def delete_sql(
    table_name: str,
    constraints: Constraints = None,
    *,
    returning: str = None) -> SQL:
  '''Generates a delete statement.

  :param table_name: the name of the table to delete from
  :param constraints: the delete constraints
  :param returning: a returning column list
  '''
  (constraint_sql, params) = constraints_to_sql(constraints)

  sql = 'delete from {}'.format(table_name)

  if constraint_sql:
    sql = '{} where {}'.format(sql, constraint_sql)

  if returning:
    sql = '{} returning {}'.format(sql, returning)

  return (sql, params)
