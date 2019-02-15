'''Contains the DB wrapper class.'''
from contextlib import (asynccontextmanager)
from typing import (Any, AsyncIterator, Callable, Optional, List, cast)
from logging import (Logger, getLogger)
from asyncpg import (Connection, connect)
import apgw.builder as builder
from apgw.constraint import (Constraints)
from apgw.types import (ConnectionArgs, InsertAssignments, LimitOffset, Record, RecordsAndCount)

class DB:
  '''A simple wrapper around asyncpg to alleviate some boilerplate.'''
  def __init__(
      self,
      conn_args: ConnectionArgs,
      *,
      auto_open: bool = False,
      logger: Logger = getLogger('apgw'),
      _connect: Callable[..., Connection] = connect,
  ) -> None:
    '''Initializes the DB instance.

    :param conn_args: the connection arguments
    :param logger: a Logger instance
    '''
    self.conn_args = conn_args
    self._auto_open = auto_open
    self.logger = logger
    self._connect = _connect
    self._conn: Optional[Connection] = None

  @property
  def is_open(self) -> bool:
    '''Returns True if the instance is connected.'''
    return bool(self._conn)

  @property
  def conn(self) -> Connection:
    if self._conn is None:
      raise Exception('Connection is not open')
    return self._conn

  @property
  def _should_auto_open(self) -> bool:
    '''Returns True if the connection can and should be opened automatically.'''
    return self._auto_open and not self.is_open

  async def auto_open(self) -> bool:
    '''Opens the database if it should auto open.'''
    if self._should_auto_open:
      await self.open()
      return True
    return False

  async def open(self) -> 'DB':
    '''Opens the connection.'''
    if not self._conn:
      if isinstance(self.conn_args, str):
        self._conn = await self._connect(dsn=self.conn_args)
      else:
        self._conn = await self._connect(**self.conn_args)
    return self

  async def close(self) -> 'DB':
    '''Closes the connection.'''
    if self._conn:
      await self._conn.close()
      self._conn = None
    return self

  @asynccontextmanager
  async def transaction(self) -> AsyncIterator['DB']:
    '''Run a command in a database transaction.'''
    await self.auto_open()
    async with self.conn.transaction():
      yield self

  async def __aenter__(self) -> 'DB':
    '''Asynchronous context manager entry point.'''
    await self.open()
    return self

  async def __aexit__(self, exc_type: type, exc: Exception, trace) -> None:
    '''Asynchronous context manager exit point.'''
    await self.close()

  def _log(self, sql: str, params: List[Any] = None) -> None:
    '''Log out sql and params.'''
    self.logger.info('SQL: %s', sql)
    if params:
      self.logger.info('PARAMS: %s', params)

  async def fetch(self, sql: Optional[str], params: List[Any] = None) -> List[Record]:
    '''This method passes through to self.conn.fetch.

    :param sql: the parameterized sql to execute
    :param params: a list of params
    '''
    if not sql:
      raise Exception('No SQL provided')

    self._log(sql, params)

    await self.auto_open()

    if params:
      return await self.conn.fetch(sql, *params)

    return await self.conn.fetch(sql)

  async def fetchrow(self, sql: Optional[str], params: List[Any] = None) -> Optional[Record]:
    '''This method passes through to self.conn.fetchrow.

    :param sql: the parameterized sql to execute
    :param params: a list of params
    '''
    if not sql:
      raise Exception('No SQL provided')

    self._log(sql, params)

    await self.auto_open()

    if params:
      return await self.conn.fetchrow(sql, *params)

    return await self.conn.fetchrow(sql)

  async def select(
      self,
      table_name: str,
      constraints: Constraints = None,
      *,
      columns: str = '*',
      order_by: str = None,
      limit: LimitOffset = None
  ) -> List[Record]:
    '''Selects records from the database.

    :param table_name: the name of the table to select from
    :param constraints: the constraints for the select filter
    :param columns: the columns to select
    :param order_by: how to order the results
    :param limit: the limit and offset of the results
    '''
    (sql, params) = builder.select_sql(
        table_name,
        constraints,
        columns=columns,
        order_by=order_by,
        limit=limit,
    )

    return await self.fetch(sql, params)

  async def select_and_count(
      self,
      table_name: str,
      constraints: Constraints = None,
      *,
      columns: str = '*',
      order_by: str = None,
      limit: LimitOffset = None
  ) -> RecordsAndCount:
    '''Counts records that match a constraint and then returns a limited set of them

    :param table_name: the name of the table to select from
    :param constraints: the constraints for the select filter
    :param columns: the columns to select
    :param order_by: how to order the results
    :param limit: the limit and offset of the results
    '''
    count_record = cast(Record, await self.select_one(
        table_name,
        constraints,
        columns='count(*) as c',
        order_by=order_by,
    ))
    records = await self.select(
        table_name,
        constraints,
        columns=columns,
        order_by=order_by,
        limit=limit,
    )
    return (records, cast(int, count_record['c']))

  async def select_one(
      self,
      table_name: str,
      constraints: Constraints = None,
      *,
      columns: str = '*',
      order_by: str = None) -> Optional[Record]:
    '''Selects a single record from the database.

    :param table_name: the name of the table to select from
    :param constraints: the constraints for the select filter
    :param columns: the columns to select
    :param order_by: how to order the results
    '''
    (sql, params) = builder.select_sql(
        table_name,
        constraints,
        columns=columns,
        order_by=order_by,
        limit=(1, None),
    )

    return await self.fetchrow(sql, params)

  async def exists(self, table_name: str, constraints: Constraints = None) -> bool:
    '''Returns True if the record exists, False otherwise.

    :param table_name: the name of the table to select from
    :param constraits: the filtering constraints
    '''
    (sql, params) = builder.select_sql(table_name, constraints)

    return await self.fetchrow(sql, params) is not None

  async def insert(
      self,
      table_name: str,
      assignments: InsertAssignments,
      *,
      returning: str = None) -> Record:
    '''Inserts a record into the database.

    :param table_name: the name of the table to insert on
    :param assignments: the insert assignments
    :param returning: a returning column list
    '''
    (sql, params) = builder.insert_sql(
        table_name,
        assignments,
        returning=returning)

    output = await self.fetchrow(sql, params)
    return cast(Record, output)

  async def create(
      self,
      table_name: str,
      assignments: InsertAssignments,
      *,
      returning: str = '*') -> Record:
    '''A wrapper around #insert with a default value on returning of '*'

    :param table_name: the name of the table to insert on
    :param assignments: the insert assignments
    :param returning: a returning column list
    '''
    if returning is None:
      raise Exception('Must specify returning')

    return await self.insert(table_name, assignments, returning=returning)

  async def update(
      self,
      table_name: str,
      assignments: Constraints,
      constraints: Constraints = None,
      *,
      timestamp_col: str = 'updated_at',
      returning: str = None) -> List[Record]:
    '''Updates records in the database.

    :param table_name: the name of the table to update
    :param assignments: the updates to make
    :param constraints: the filter for the updates
    :param timestamp_col: the 'updated_at' column, if any
    :param returning: the list of colums to return from the update statement
    '''
    (sql, params) = builder.update_sql(
        table_name,
        assignments,
        constraints,
        timestamp_col=timestamp_col,
        returning=returning)

    return await self.fetch(sql, params)

  async def delete(
      self,
      table_name: str,
      constraints: Constraints = None,
      *,
      returning: str = None) -> List[Record]:
    '''Deletes records from the database.

    :param table_name: the name of the table to delete from
    :param constraints: the delete constraints
    :param returning: a returning column list
    '''
    (sql, params) = builder.delete_sql(
        table_name,
        constraints,
        returning=returning)

    return await self.fetch(sql, params)
