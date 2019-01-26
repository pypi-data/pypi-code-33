import json
from datetime import timezone

import sql.functions
from MySQLdb import (
  connect, constants, converters, cursors, connections, ProgrammingError, OperationalError)

from . import AbstractStorage


class Storage(AbstractStorage):

  @staticmethod
  def _createConverters():
    result = converters.conversions.copy()

    def wrapDt(key):
      orig = result[key]
      def wrapper(s):
        r = orig(s)
        return r.replace(tzinfo = timezone.utc) if r else r

      result[key] = wrapper

    wrapDt(constants.FIELD_TYPE.DATETIME)
    wrapDt(constants.FIELD_TYPE.TIMESTAMP)

    # At the time of writing JSON type is not defined in the mysqlclient's module
    MYSQL_TYPE_JSON = 245
    result[MYSQL_TYPE_JSON] = json.loads

    return result

  def _createConnection(self):
    sql.Flavor.set(sql.Flavor(paramstyle = 'format'))
    return connect(
      host         = self._config.hostname,
      user         = self._config.username,
      password     = self._config.password or '',
      database     = self._config.path.strip('/'),
      port         = self._config.port or 3306,
      charset      = 'utf8mb4',
      conv         = self._createConverters(),
      autocommit   = True,
      cursorclass  = ReconnectingDictCursor,
      init_command = "SET sql_mode = (SELECT CONCAT(@@sql_mode, ',ANSI_QUOTES'))"
    )

  def _isSqlSyntaxError(self, ex):
    return (
      isinstance(ex, ProgrammingError)
      or isinstance(ex, OperationalError) and ex.args[0] == 3143  # Invalid JSON path expression
    )

  def _applyCountGroup(self, query, group):
    if group:
      query.columns += (
        FromUnixtime(sql.functions.Floor(UnixTimestamp(self._table.ts) / 900) * 900).as_('group'),)
      query.group_by = sql.Literal(2)

    return query

  def _resolveInsertedIds(self, records, cursor):
    assert cursor.rowcount == len(records), 'Affected rows do not match records'
    # MySQL InnoDB guarantees sequential auto-increment ids in single statement
    # https://dev.mysql.com/doc/refman/5.7/en/innodb-auto-increment-handling.html.
    # For multi-value INSERTs lastrowid evaluated to the id of the first inserted row.
    for i, id in enumerate(range(cursor.lastrowid, cursor.lastrowid + cursor.rowcount)):
      records[i].id = id


class ReconnectingDictCursor(cursors.DictCursor):
  '''Cursor that reconnects once on lost, timed out connection.
  As long as the package uses only simple auto-commit queries it's
  possible to follow simple retry approach on timeout.'''

  def execute(self, query, args = None):
    try:
      return super().execute(query, args)
    except connections.OperationalError as ex:
      # MySQL timeout errors:
      #   * (2006, 'MySQL server has gone away')
      #   * (2013, 'Lost connection to MySQL server during query')
      if ex.args[0] in (2006, 2013):
        try:
          # On Unix socket connection two pings as below are sufficient, unlike on TCP socket
          self.connection.ping(False)
        except connections.OperationalError:
          # See http://mysqlsimplequerybuilder.rtfd.io/en/latest/design.html#persistent-connection
          self.connection.ping(True)
          self.connection.ping(False)

        return super().execute(query, args)
      else:
        raise


class FromUnixtime(sql.functions.Function):

  __slots__ = ()

  _function = 'FROM_UNIXTIME'


class UnixTimestamp(sql.functions.Function):

  __slots__ = ()

  _function = 'UNIX_TIMESTAMP'

