import json
import threading
from datetime import datetime, timezone
from urllib.parse import urlparse

import sql.aggregate
from clor import resolve

from ..model import Record


__all__ = 'createStorage', 'StorageError', 'StorageQueryError', 'AbstractStorage'


def createStorage(dsn):
  if not dsn:
    raise ValueError('Empty storage DSN')

  cfg = urlparse(dsn)
  scheme = cfg.scheme.split('+', 1)
  driver = scheme[1].title() if scheme[1:] else 'Storage'
  cls = resolve('.'.join(['chronologer', 'storage', scheme[0], driver]))
  return cls(cfg)


class StorageError(Exception):
  '''Generic storage error'''


class StorageQueryError(StorageError):
  '''The exception indicates invalid storage query input'''


class AbstractStorage:

  _table = sql.Table('record')
  '''Record table'''

  _config = None
  '''URL-parsed DSN'''

  _local = None
  '''Thread local'''


  def __init__(self, config):
    self._config = config
    self._local = threading.local()

  @property
  def _db(self):
    if not hasattr(self._local, 'db'):
      self._local.db = self._createConnection()

    return self._local.db

  def _createConnection(self):
    raise NotImplementedError

  def _applyFilters(self, query, values):
    if values['name']:
      query.where &= sql.operators.Or([
        self._table.name.like(n + '%')
        for n in map(str.strip, values['name'].split(','))])

    if values['level']:
      query.where &= self._table.level >= values['level']

    if values['date'][0]:
      query.where &= self._table.ts >= values['date'][0]

    if values['date'][1]:
      query.where &= self._table.ts <= values['date'][1]

    if values['query']:
      query.where &= Raw(values['query'])

    return query

  def _applyCountGroup(self, sql, group):
    raise NotImplementedError

  def _resolveInsertedIds(self, records, cursor):
    raise NotImplementedError

  def _isSqlSyntaxError(self, ex):
    raise NotImplementedError

  def count(self, filters, group = False):
    '''Return number of records matching given filters. If ``group`` is true
    return number per 15 minute intervals. 15 minute intervals allow grouping
    for arbitrary timezone. For instance, it could be implemented on MySQL
    side as well with a timezone-aware TIMESTAMP column and loaded timezone
    data. But this seems a hard requirement on storage.'''

    query = self._table.select(
      sql.aggregate.Count(sql.Literal(1)).as_('count'),
      where = sql.Literal(1))
    query = self._applyFilters(query, filters)
    query = self._applyCountGroup(query, group)

    cursor = self._db.cursor()
    try:
      cursor.execute(*query)
    except Exception as ex:
      if self._isSqlSyntaxError(ex):
        raise StorageQueryError('Make sure the query filter is a valid WHERE expression')
      else:
        raise

    if group:
      return tuple((r['group'], r['count']) for r in cursor.fetchall())
    else:
      return cursor.fetchone()['count']

  def range(self, left, right, filters):
    query = self._table.select(
      self._table.record_id.as_('id'),
      self._table.name,
      self._table.ts,
      self._table.level,
      self._table.message,
      self._table.logrec,
      where = sql.Literal(1),
      order_by = self._table.record_id.desc,
      limit = right - left + 1, offset = left)
    query = self._applyFilters(query, filters)

    cursor = self._db.cursor()
    try:
      cursor.execute(*query)
    except Exception as ex:
      if self._isSqlSyntaxError(ex):
        raise StorageQueryError('Make sure the query filter is a valid WHERE expression')
      else:
        raise

    return [Record(**r) for r in cursor]

  def get(self, id):
    query = self._table.select(
      self._table.record_id.as_('id'),
      self._table.name,
      self._table.ts,
      self._table.level,
      self._table.message,
      self._table.logrec,
      where = self._table.record_id == id)

    cursor = self._db.cursor()
    cursor.execute(*query)
    row = cursor.fetchone()
    if row:
      return Record(**row)

  def record(self, records):
    query = self._table.insert(
      columns = [
        self._table.name,
        self._table.ts,
        self._table.level,
        self._table.message,
        self._table.logrec
      ],
      values = [
        (r.name, r.ts, r.level, r.message, json.dumps(r.logrec, default = str)) for r in records]
    )

    cursor = self._db.cursor()
    if len(records) == 1:
      cursor.execute(*query)
      records[0].id = cursor.lastrowid
    elif len(records) > 1:
      cursor.execute(*query)
      self._resolveInsertedIds(records, cursor)

    return records

  def purge(self, older):
    '''Delete records older than given ``timedelta``.'''

    query = self._table.delete(where = self._table.ts < datetime.now(timezone.utc) - older)

    cursor = self._db.cursor()
    cursor.execute(*query)

    return cursor.rowcount


class Raw(sql.Expression):

  __slots__ = ('value')


  def __init__(self, value):
    super().__init__()
    self.value = value

  @property
  def params(self):
    return ()

  def __str__(self):
    return self.value

