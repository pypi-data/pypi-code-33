# coding=utf-8
import psycopg2
import logging

logger = logging.getLogger(__name__)

DROP_SCHEMA = u'DROP SCHEMA IF EXISTS {} CASCADE'
CREATE_SCHEMA = u'CREATE SCHEMA {}'

class Postgres(object):

    def __init__(self, user, password, hostname, port, dbname):
        conn_string = 'host=\'{}\' port=\'{}\' dbname=\'{}\' user=\'{}\' password=\'{}\''.format(hostname, port, dbname, user, password)
        self._connection = psycopg2.connect(conn_string)

    def _execute(self, statement_str):
        with self._connection:  # transaction
            with self._connection.cursor() as cursor:
                cursor.execute(statement_str)

    def drop_existing_schema(self, schema_name):
        logger.debug('Dropping schema {}'.format(schema_name))
        self._execute(DROP_SCHEMA.format(schema_name))

    def create_new_schema(self, schema_name):
        logger.debug('Creating schema {}'.format(schema_name))
        self._execute(CREATE_SCHEMA.format(schema_name))