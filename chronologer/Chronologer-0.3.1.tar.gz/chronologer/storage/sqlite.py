import json
import sqlite3
from datetime import datetime, timezone

import sql

from . import AbstractStorage, Raw


class RecordTable(sql.Table):
  '''Because ``sqlite3.PARSE_DECLTYPES`` only works on raw columns,
  this class provides automatic SQLite-specific type aliases for columns
  that have corresponding converters registered.'''

  _types = {
    'ts'     : 'DATETIME',
    'logrec' : 'JSON'
  }


  def select(self, *args, **kwargs):
    columns = []
    for c in args:
      if isinstance(c, sql.Column) and c.name in self._types:
        c = c.as_('{} [{}]'.format(c.name, self._types[c.name]))
      columns.append(c)

    return super().select(*columns, **kwargs)


class Storage(AbstractStorage):

  _table = RecordTable('record')


  def _createConnection(self):
    sql.Flavor.set(sql.Flavor(paramstyle = 'qmark'))

    sqlite3.register_converter('json', lambda b: json.loads(b.decode()))

    # float is not used because of a rounding issue which is only present with registered converter
    sqlite3.register_converter(
      'datetime', lambda b: datetime.utcfromtimestamp(
        int(b) / 10 ** 6).replace(tzinfo = timezone.utc))
    sqlite3.register_adapter(datetime, lambda dt: int(datetime.timestamp(dt) * 10 ** 6))

    uri = 'file:{}?{}'.format(self._config.path[1:], self._config.query)
    result = sqlite3.connect(
      database = uri, uri = True, isolation_level = None, detect_types = sqlite3.PARSE_COLNAMES)
    result.row_factory = sqlite3.Row
    return result

  def _isSqlSyntaxError(self, ex):
    return isinstance(ex, sqlite3.OperationalError) and any(s in str(ex) for s in (
      'syntax error', 'unrecognized token', 'JSON path error',
      'no such function', 'wrong number of arguments to function'))

  def _applyCountGroup(self, query, group):
    if group:
      m15ms = 15 * 60 * 10 ** 6
      query.columns += ((self._table.ts / m15ms * m15ms).as_('group [DATETIME]'),)
      query.group_by = Raw('2')

    return query

  def _resolveInsertedIds(self, records, cursor):
    assert cursor.rowcount == len(records), 'Affected rows do not match records'
    # SQLite doesn't have a documentation on guarantees about sequential
    # auto-generated ids in a single INSERT statement. Neither it states the other.
    # For the time being it's assumed that because a SQLite database can have only
    # one writer at a time, the ids are sequential.
    # For multi-value INSERTs lastrowid evaluated to the id of the last inserted row.
    for i, id in enumerate(range(cursor.lastrowid - cursor.rowcount + 1, cursor.lastrowid + 1)):
      records[i].id = id

