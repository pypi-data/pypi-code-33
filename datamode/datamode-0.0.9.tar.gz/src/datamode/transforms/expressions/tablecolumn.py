from collections import namedtuple
from datamode.errors import ColumnNotFoundError, AmbiguousColumnError

from datamode.utils.utils import get_logger
log = get_logger(__name__)


TableColumn = namedtuple('TableColumn', 'table column')


# Utility class to manage tables and columns and their relationship to the working dataset.
class TableColumnManager():
  def __init__(self, current_tcon_table, working_dfs):
    self.current_tcon_table = current_tcon_table
    self.working_dfs = working_dfs

    # Doesn't include any destination tables (by design)
    self.source_tables_seen = set()

    # Cache that maps a bare column to its table.
    self.bare_column_tables = {}

  # destinationExpr expects a pyparsing.parseResults with either column or tableColumn populated.
  def get_destination_tablecolumn(self, destinationExpr):
    tc = self.get_tablecolumn_from_raw_construct(destinationExpr)

    # If the table isn't specified:
    #   If there's a single table seen so far, use that, e.g. total = price + tax + fees.
    #   If there's more than one table, raise.
    if tc.table is None:
      # If table isn't present, that means the bare column wasn't found in any of the existing tables.
      if len(self.source_tables_seen) == 1:
        table = next(iter(self.source_tables_seen))
        tc = TableColumn(table, tc.column)
      else:
        raise Exception(f'TableColumnManager: ambiguous destination table. Seen tables: {self.source_tables_seen}')


    return tc

  # Note: tc.table can be None if validation is False
  def get_tablecolumn_from_raw_construct(self, construct, validate_column_exists=False):
    table, column = self.extract_from_raw_construct(construct)

    # If we're looking at a primitive or any non-tablecolumn construct, there won't be a column to look up.
    if table is None and column is None:
      return None

    table, column = self.populate_table_if_possible(table, column)

    if validate_column_exists and table is None:
      raise ColumnNotFoundError(f'Expression: column "{column}" not found in existing tables.')

    self.note_source_table(table)
    return TableColumn(table, column)


  def note_source_table(self, table):
    if table is not None and table not in self.source_tables_seen:
      # log.debug(f'Using source table {table}')
      self.source_tables_seen.add(table)


  # Parses a column/tablecolumn construct into a bare table, column tuple.
  def extract_from_raw_construct(self, construct):
    tableColumn = construct.get('tableColumn')
    column = construct.get('column')

    if tableColumn:
      return tableColumn.table, tableColumn.column
    elif column:
      column = construct['column']
      return None, column
    else:
      # todo: this shouldn't happen - consider raising instead?
      return None, None


  def populate_table_if_possible(self, table, column):
    # If we don't have the table yet, find it in our existing dataset.
    if not table:
      table = self.get_table_for_column(column)

    return table, column


  # Returns the single table for a given column.
  # Will return None if there is no matching table, or raise an error if the column was ambiguous.
  def get_table_for_column(self, column):
    # If we haven't resolved the table, do that first.
    # The algorithm can legitimately store None, so we won't do a lookup twice.
    if column not in self.bare_column_tables:
      self.bare_column_tables[column] = self.get_table_for_column_inner(column)

    return self.bare_column_tables[column]

  # The uncached worker function.
  def get_table_for_column_inner(self, column):
    df_names_with_column = []
    for df_name, df in self.working_dfs.items():
      if column in df.columns:
        df_names_with_column.append(df_name)

    count = len(df_names_with_column)
    if count == 1:
      return df_names_with_column[0]

    # We either have an ambiguous column or no column.
    df_names = [df_name for df_name, df in self.working_dfs.items()]
    if count == 0:
      return None
    else:
      raise AmbiguousColumnError('Expression: ambiguous column - please provide a fully qualified column, e.g. "yourtable.yourcolumn".')

  def __str__(self):
    return f'sources={self.working_dfs.keys()}, seen={self.source_tables_seen} current_table={self.current_tcon_table}'

  def __repr__(self):
    return f'<{type(self).__name__}: {str(self)}>'
