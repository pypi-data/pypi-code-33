import sqlite3


def dict_factory(cursor, row):
    """Make sqlite3 query return dict instead of tuple list."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SqlDict(object):
    def __init__(self, filename):
        self.dbname = filename

    def _open(self):
        self.db = sqlite3.connect(self.dbname)

        # Enable autocommit
        self.db.isolation_level = None
        self.db.row_factory = dict_factory
        self.cursor = self.db.cursor()

    def _close(self):
        self.db.close()
        self.db = None
        self.cursor = None

    def table(self, table_name):
        return SqlDictTable(self, table_name)

    def _ensure_table(self, table_name, data):
        """Create or alter table according to data to ensure data is insertable."""
        sql = "SELECT tbl_name FROM sqlite_master WHERE tbl_name=?"
        self.cursor.execute(sql, (table_name,))
        tbl = self.cursor.fetchone()

        if tbl is None:
            self._create_table(table_name, data)
        else:
            self._alter_table(table_name, data)

    def _insert_data(self, table_name, data):
        """Insert data into table_name."""
        sql = "INSERT INTO `%s` (%s) VALUES (%s)" % (
            table_name,
            ', '.join("`%s`" % k for k in data.keys()),
            ', '.join(['?'] * len(data)),
        )
        try:
            self.cursor.execute(sql, list(data.values()))
        except sqlite3.OperationalError:
            self._ensure_table(table_name, data)
            self.cursor.execute(sql, list(data.values()))

    def _infer_columns_from_data(self, data):
        """Infer column types from given data."""
        columns = {}
        for k, v in data.items():
            if isinstance(v, str):
                column_type = 'TEXT'
            elif isinstance(v, int):
                column_type = 'INTEGER'
            elif isinstance(v, float):
                column_type = 'REAL'
            else:
                raise TypeError('Unsupported value type: %s' % type(v).__name__)
            columns[k] = column_type

        return columns

    def _columns_to_sql(self, columns):
        """Join column definitions into SQL expression."""
        return ', '.join('%s %s' % (k, v) for k, v in columns.items())

    def _get_table_columns(self, table_name):
        """Get the column map for an existing table."""
        sql = 'PRAGMA table_info(%s)' % table_name
        self.cursor.execute(sql)
        columns = self.cursor.fetchall()
        return {c['name']: c['type'] for c in columns}

    def _create_table(self, table_name, data):
        """Create table from given data."""
        columns = self._infer_columns_from_data(data)
        sql = 'CREATE TABLE `%s` (_id INTEGER PRIMARY KEY AUTOINCREMENT, %s)' % (
            table_name, self._columns_to_sql(columns))
        self.cursor.execute(sql)

    def _alter_table(self, table_name, data):
        """Alter table to accomodate given data."""
        columns = self._infer_columns_from_data(data)
        existing_columns = self._get_table_columns(table_name)

        for column_name, column_type in columns.items():
            if column_name not in existing_columns:
                sql = 'ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type)
                self.cursor.execute(sql)

    def _select_data(self, table_name: str, exclude_auto_id=False, **args):
        """Query data with given criteria."""
        keys = list(args.keys())
        values = [args[k] for k in keys]
        sql = 'SELECT * FROM `%s`' % table_name
        if keys:
            criteria = ' AND '.join(['%s=?' % k for k in keys])
            sql = sql + ' WHERE ' + criteria

        self.cursor.execute(sql, values)
        data = self.cursor.fetchall()

        # filter out None values
        data = [{k: v for k, v in d.items() if v is not None} for d in data]

        # filter out auto id (_id)
        if exclude_auto_id:
            data = [{k: v for k, v in d.items() if k != '_id'} for d in data]

        return data


class SqlDictTable(object):
    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name

    def put(self, obj):
        """Put object into table."""
        self.db._open()
        self.db._insert_data(self.table_name, obj)
        self.db._close()

    def put_multi(self, objs):
        """Put multiple objects into table."""
        self.db._open()
        for obj in objs:
            self.db._insert_data(self.table_name, obj)
        self.db._close()

    def get(self, exclude_auto_id=False, **args):
        """Get the first object using given criteria."""
        objs = self.filter(exclude_auto_id=exclude_auto_id, **args)
        if objs:
            return objs[0]
        else:
            return None

    def filter(self, exclude_auto_id=False, **args):
        """Get all objects using given criteria."""
        self.db._open()
        objs = self.db._select_data(self.table_name, exclude_auto_id=exclude_auto_id, **args)
        self.db._close()
        return objs
