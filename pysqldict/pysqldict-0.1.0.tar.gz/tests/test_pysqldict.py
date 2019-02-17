import unittest
from unittest.mock import patch

import pysqldict
from pysqldict import SqlDict


class PackageTestCase(unittest.TestCase):
    def test_open(self):
        """Should create a new database and return its reference."""
        db = pysqldict.open(':memory:')
        self.assertTrue(isinstance(db, SqlDict))


class SqlDictBasicTestCase(unittest.TestCase):

    def setUp(self):
        self.db = SqlDict(':memory:')

    def test_open(self):
        """Should open db instance and create cursor."""
        self.db._open()
        self.assertTrue(self.db.db)
        self.assertTrue(self.db.cursor)
        self.db._close()

    def test_close(self):
        """Should close db instance and remove cursor reference."""
        self.db._open()
        self.db._close()
        self.assertIsNone(self.db.db)
        self.assertIsNone(self.db.cursor)

    def test_table(self):
        """Should create table object."""
        table = self.db.table('t1')
        self.assertTrue(table)


class SqlDictSqlTestCase(unittest.TestCase):

    def setUp(self):
        self.db = SqlDict(':memory:')
        self.db._open()

    def tearDown(self):
        self.db._close()

    @patch('pysqldict.SqlDict._create_table')
    def test_ensure_table_create(self, mock_create_table):
        """Should call _create_table."""
        self.db._ensure_table('t1', {'a': 1})
        self.assertTrue(mock_create_table.called)

    @patch('pysqldict.SqlDict._alter_table')
    def test_ensure_table_alter(self, mock_alter_table):
        """Should call _alter_table."""
        self.db._ensure_table('t1', {'a': 1})
        self.db._ensure_table('t1', {'b': 2})
        self.assertTrue(mock_alter_table.called)

    def assertDbColumns(self, table_name, expected_columns):
        """Helper function for testing db table columns."""
        self.db.cursor.execute('PRAGMA table_info(%s)' % table_name)
        columns = self.db.cursor.fetchall()
        columns = [{'name': c['name'], 'type': c['type'], 'pk': c['pk']} for c in columns]
        columns.sort(key=lambda c: c['name'])
        self.assertListEqual(columns, expected_columns)

    def test_create_table(self):
        """Should create table based on given data."""
        self.db._create_table('t1', {'int': 1, 'text': 'hello', 'float': 1.5})
        self.assertDbColumns('t1', [
            {'name': '_id', 'type': 'INTEGER', 'pk': 1},
            {'name': 'float', 'type': 'REAL', 'pk': 0},
            {'name': 'int', 'type': 'INTEGER', 'pk': 0},
            {'name': 'text', 'type': 'TEXT', 'pk': 0},
        ])

    def test_alter_table(self):
        """Should change table based on given data."""
        self.db._create_table('t1', {'int2': 1})
        self.db._alter_table('t1', {'text2': 'hello', 'float2': 1.5})
        self.assertDbColumns('t1', [
            {'name': '_id', 'type': 'INTEGER', 'pk': 1},
            {'name': 'float2', 'type': 'REAL', 'pk': 0},
            {'name': 'int2', 'type': 'INTEGER', 'pk': 0},
            {'name': 'text2', 'type': 'TEXT', 'pk': 0},
        ])

    def test_infer_columns_from_data(self):
        data = {'int': 1, 'text': 'hello', 'float': 1.5}
        columns = self.db._infer_columns_from_data(data)
        self.assertDictEqual(columns, {
            'float': 'REAL',
            'int': 'INTEGER',
            'text': 'TEXT',
        })

    def test_infer_columns_from_data_exception(self):
        data = {'list': [1, 2, 3]}
        with self.assertRaises(TypeError):
            self.db._infer_columns_from_data(data)

    def test_columns_to_sql(self):
        columns = {
            'float': 'REAL',
            'int': 'INTEGER',
            'text': 'TEXT',
        }
        sql = self.db._columns_to_sql(columns)
        self.assertIn('float REAL', sql)
        self.assertIn('int INTEGER', sql)
        self.assertIn('text TEXT', sql)

    def test_insert_data(self):
        """_insert_data should create table automatically."""
        data = {'int': 1, 'text': 'hello', 'float': 1.5}
        self.db._insert_data('t2', data)
        self.db.cursor.execute('SELECT int, text, float FROM t2')
        result = self.db.cursor.fetchone()
        self.assertDictEqual(result, data)

    def test_insert_data_alter_table(self):
        """_insert_data should alter table automatically."""
        data1 = {'int': 1, 'text': 'hello', 'float': 1.5}
        self.db._insert_data('t2', data1)

        data2 = dict(data1)
        data2.update({'other': 'test'})
        self.db._insert_data('t2', data2)

        self.db.cursor.execute('SELECT int, text, float, other FROM t2')
        results = self.db.cursor.fetchall()

        data1_expected = dict(data1)
        data1_expected.update({'other': None})

        self.assertDictEqual(results[0], data1_expected)
        self.assertDictEqual(results[1], data2)

    def test_select_data(self):
        data = [
            {'int': 1, 'text': 'hello', 'float': 1.5},
            {'int': 2, 'text': 'hello 2', 'float': 2.5},
        ]
        for d in data:
            self.db._insert_data('t1', d)
        results = self.db._select_data('t1')
        self.assertTrue(set(data[0].items()) <= set(results[0].items()))
        self.assertTrue(set(data[1].items()) <= set(results[1].items()))

    def test_select_data_exclude_auto_id(self):
        data = [
            {'int': 1, 'text': 'hello', 'float': 1.5},
            {'int': 2, 'text': 'hello 2', 'float': 2.5},
        ]
        for d in data:
            self.db._insert_data('t1', d)
        results = self.db._select_data('t1', exclude_auto_id=True)
        self.assertDictEqual(data[0], results[0])
        self.assertDictEqual(data[1], results[1])


class SqlDictTableTestCase(unittest.TestCase):

    def setUp(self):
        self.db = SqlDict(':memory:')
        self.table = self.db.table('t1')

    @patch('pysqldict.SqlDict._close')
    def test_put(self, mock_close):
        """put should store an object into the database."""
        data = {'int': 1, 'text': 'hello', 'float': 1.5}
        self.table.put(data)
        results = self.db._select_data('t1', exclude_auto_id=True)
        self.assertDictEqual(results[0], data)

    @patch('pysqldict.SqlDict._close')
    def test_put_multi(self, mock_close):
        data = [
            {'int': 1, 'text': 'hello', 'float': 1.5},
            {'int': 2, 'text': 'hello 2', 'float': 2.5},
        ]
        self.table.put_multi(data)
        results = self.db._select_data('t1', exclude_auto_id=True)
        self.assertDictEqual(results[0], data[0])
        self.assertDictEqual(results[1], data[1])

    def test_get(self):
        data = {'int': 1, 'text': 'hello', 'float': 1.5}
        self.db._open()
        self.db._insert_data('t1', data)

        with unittest.mock.patch('pysqldict.SqlDict._open'):
            result = self.table.get(exclude_auto_id=True)
            self.assertDictEqual(result, data)

    def test_filter(self):
        data = [
            {'int': 1, 'text': 'hello', 'float': 1.5},
            {'int': 2, 'text': 'hello 2', 'float': 2.5},
        ]
        self.db._open()
        for d in data:
            self.db._insert_data('t1', d)

        with unittest.mock.patch('pysqldict.SqlDict._open'):
            results = self.table.filter(exclude_auto_id=True)
            self.assertDictEqual(results[0], data[0])
            self.assertDictEqual(results[1], data[1])

    def test_filter_multi_criteria(self):
        data = [
            {'int': 1, 'text': 'hello', 'float': 1.5},
            {'int': 2, 'text': 'hello', 'float': 2.5},
            {'int': 3, 'text': 'hello 3', 'float': 3.5},
        ]

        self.db._open()
        for d in data:
            self.db._insert_data('t1', d)

        with unittest.mock.patch('pysqldict.SqlDict._open'):
            results = self.table.filter(text='hello', int=2, exclude_auto_id=True)
            self.assertDictEqual(results[0], data[1])

    def test_get_with_null_output(self):
        data = {'int': 1, 'text': 'hello', 'float': 1.5}
        self.db._open()
        self.db._insert_data('t1', data)

        with unittest.mock.patch('pysqldict.SqlDict._open'):
            result = self.table.get(int=2, exclude_auto_id=True)
            self.assertIsNone(result)
