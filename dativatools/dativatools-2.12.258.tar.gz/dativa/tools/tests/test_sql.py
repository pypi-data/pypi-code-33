import unittest
import logging
from io import StringIO
from os import path
import sqlite3
from dativa.tools import SqlClient


logger = logging.getLogger("dativa.tools.sql.tests")


class SqlTest(unittest.TestCase):

    def setUp(self):

        self.base_path = "{0}/test_data/sqlclient/".format(
            path.dirname(path.abspath(__file__)))

        # set up the SQL Lite database
        self.connection = sqlite3.connect(":memory:")

        # enable log capture
        self.log_stream = StringIO()
        sql_logger = logging.getLogger("dativa.tools.sql_client")
        handler = logging.StreamHandler(self.log_stream)
        handler.setFormatter(logging.Formatter('%(message)s'))
        sql_logger.addHandler(handler)

    def test_execute_df(self):
        sql = SqlClient(self.connection)
        sql.execute_query("{0}create_table.sql".format(self.base_path))

        df = sql.execute_query_to_df("SELECT * FROM test")

        self.assertEqual(df.ix[0, 0], 'bee bee')
        self.assertEqual(df.ix[0, 1], 374)
        self.assertEqual(df.shape, (1, 2))
        self.assertEqual(self.log_stream.getvalue()[-17:], "1 rows affected\n\n")

    def test_execute_df_replace(self):
        sql = SqlClient(self.connection)
        sql.execute_query("{0}create_table.sql".format(self.base_path),
                          replace={"bee bee": "boo boo"})

        df = sql.execute_query_to_df("SELECT * FROM test;")

        self.assertEqual(df.ix[0, 0], 'boo boo')
        self.assertEqual(df.ix[0, 1], 374)
        self.assertEqual(df.shape, (1, 2))
        self.assertEqual(self.log_stream.getvalue()[-17:], "1 rows affected\n\n")

        df = sql.execute_query_to_df(
            "UPDATE test set name='' WHERE name = 'boo boo';SELECT * FROM test WHERE name ='';")

        self.assertEqual(df.ix[0, 0], '')
        self.assertEqual(df.ix[0, 1], 374)
        self.assertEqual(df.shape, (1, 2))
        self.assertEqual(self.log_stream.getvalue()[-17:], "1 rows affected\n\n")

        df = sql.execute_query_to_df("UPDATE test set name='baa' WHERE name = '';SELECT * FROM test WHERE name ='';")

        self.assertEqual(df.shape, (0, 0))
        self.assertEqual(self.log_stream.getvalue()[-20:], "No results returned\n")

    def test_execute_csv(self):
        sql = SqlClient(self.connection)
        sql.execute_query("{0}create_table.sql".format(self.base_path))

        sql.execute_query_to_csv("SELECT * FROM test", "{0}sql_test_output.csv".format(self.base_path))

        with open("{0}sql_test_output.csv".format(self.base_path)) as file_out:
            with open("{0}sql_test_input.csv".format(self.base_path)) as file_in:
                self.assertEqual(file_out.read(), file_in.read())

        sql.execute_query_to_csv("SELECT * FROM test", "{0}sql_test_output.csv".format(self.base_path), append=True)

        with open("{0}sql_test_output.csv".format(self.base_path)) as file_out:
            with open("{0}sql_test_input_append.csv".format(self.base_path)) as file_in:
                self.assertEqual(file_out.read(), file_in.read())

        sql.execute_query_to_csv("SELECT * FROM test", "{0}sql_test_output.csv".format(self.base_path))

        with open("{0}sql_test_output.csv".format(self.base_path)) as file_out:
            with open("{0}sql_test_input.csv".format(self.base_path)) as file_in:
                self.assertEqual(file_out.read(), file_in.read())

    def test_exception(self):
        sql = SqlClient(self.connection)
        try:
            sql.execute_query("{0}file_not_found.sql".format(self.base_path))
        except OSError:
            self.assertTrue(True)
            return

        self.assertTrue(False)
