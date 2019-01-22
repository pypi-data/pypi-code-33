#!/usr/bin/env python

import os
import re
import boto3
import logging
import psycopg2
import sqlparse
import pymysql
import json
import time
import botocore.exceptions
from .file import ConfigFile
from .logger import Logger
from psycopg2.extras import NamedTupleCursor
from datetime import datetime
from .extras import get_current_timestamp, MILLIS_FORMAT


logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('boto3').setLevel(logging.ERROR)


class MySQL(object):
    def __init__(self, host, user, password, database, port, charset='UTF8', cursor_factory=pymysql.cursors.DictCursor, autocommit=True, level='INFO'):
        """
        Constructor
        :param host: Host [String]
        :param user: User [String]
        :param password: Password [String]
        :param database: Database name to connect [String]
        :param port: Port number [Integer]
        :param charset: Charset. Default UTF-8 [String]
        :param cursor_factory: Type of cursor, DictCursor or NamedTupleCursor (Default) [Cursor]
        :param autocommit: Enable or disable autocommit [Boolean]
        :param level: logging level [String]
        """
        self._logger = Logger(logger_name=__name__ + '.mysql', level=level)
        settings = {"host": host,
                    "user": user,
                    "password": password,
                    "database": database,
                    "port": port,
                    "charset" : charset,
                    "cursorclass": cursor_factory}

        self._settings = settings
        self._autocommit = autocommit
        self._connection = self._connect()
        self._cursor = self._get_cursor(cursor_factory)

    def _connect(self):
        """
        Connect to MySQL database
        :return: Connection object [Connection]
        """
        try:
            conn = pymysql.connect(**self._settings)
            conn.autocommit = self._autocommit
            return conn
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def _get_cursor(self, cursor_factory):
        """
        Get a cursor
        :param cursor_factory: Type of cursor, NamedTupleCursor or DictCursor [CursorType]
        :return: Cursor [Cursor]
        """
        try:
            cursor = self._connection.cursor()
            return cursor
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def commit(self):
        """
        Commit transactions
        :return: None
        """
        try:
            if self._autocommit:
                self._logger.warning('Autocommit option is enabled. Sineipping commit.')
            else:
                self._connection.commit()
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def close(self):
        """
        Close connection
        :return: None
        """
        try:
            self._connection.close()
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_settings(self, key):
        """
        Get settings by key
        :param key: key [String]
        :return: Value corresponding to the key provided [String, List, Dictionary]
        """
        value = None
        if key in self._settings and key != 'password':
            value = self._settings[key]
        return value

    def insert(self, into_table=None, from_table=None, **kwargs):
            """
            Generate INSERT statement
            :param into_table: Target table name with schema [String]
            :param from_table: From table name with schema [String]
            :param kwargs: Fields mapping between target and from table, or mapping between columns and values [Dictionary]
            :return: Data, Token and Rows affected [Dictionary]
            """
            try:
                if not into_table:
                    raise Exception('Missing target table')

                # Listing values and fields
                l_values = list()
                l_fields = list()

                if len(kwargs) == 0:
                    cmd = 'INSERT INTO {into_table} '
                    l_values.append('*')
                else:
                    cmd = 'INSERT INTO {into_table} ({into_fields}) '
                    for arg in kwargs:
                        l_fields.append(arg)
                        value = str(kwargs[arg])
                        if not from_table:
                            try:
                                long(value)
                            except Exception:
                                try:
                                    float(value)
                                except Exception:
                                    value = "'{}'".format(value)
                                    pass
                                pass
                            l_values.append(value)
                        else:
                            l_values.append(kwargs[arg])

                if from_table:
                    cmd += 'SELECT {from_fields} FROM {from_table};'
                else:
                    cmd += 'VALUES ({from_fields});'

                into_fields = ', '.join(l_fields)
                from_fields = ', '.join(l_values)

                cmd = cmd.format(into_table=into_table, into_fields=into_fields,
                                 from_fields=from_fields, from_table=from_table)

                return self.execute(cmd)
            except Exception as ex:
                self._logger.error(repr(ex))
                raise

    def drop(self, table):
        """
        Drop Redshift table
        :param table: Table name with schema [String]
        :return: Data, Token and Rows affected [Dictionary]
        """
        cmd = "DROP TABLE IF EXISTS {};".format(table)
        return self.execute(cmd)

    def truncate(self, table):
        """
        Truncate Redshift table
        :param table: Table name with schema [String]
        :return: Data, Token and Rows affected [Dictionary]
        """
        cmd = "TRUNCATE {};".format(table)
        return self.execute(cmd)

    def get_columns_name(self, table, schema=None):
        """
        Get columns name for a given table
        :param table: Table name [String]
        :param schema: Schema name. None value for temp tables [String]
        :return: List of columns name [List<String>]S
        """
        query = """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = '{}'
                    AND table_schema LIKE '{}'
                    ORDER BY ordinal_position;
                """

        if schema:
            schema = '%{}%'.format(schema)
        else:
            schema = '%_temp_%'

        query = query.format(table, schema)
        result = self.execute(query.format(table, schema))

        l_columns = list()
        for row in result['data']:
            l_columns.append(row.column_name)
        return l_columns

    def execute(self, query):
        """
        Execute simple query
        :param query: query script [String]
        :return: Data, Token and Rows affected [Dictionary]
        """
        def get_table_from_query(script):
            index = 0
            tablename = None
            lines = script.split()
            while index < len(lines):
                if lines[index] in ('INTO', 'APPEND'):
                    if lines[index + 1].upper() == 'TEMP':
                        tablename = lines[index + 2].replace(';', '')
                    elif lines[index + 1].upper() == 'FROM':
                        tablename = lines[index + 2].replace(';', '')
                    else:
                        tablename = lines[index + 1].replace(';', '')
                    index = len(lines)
                else:
                    index += 1
            return tablename

        try:
            query = query.strip()
            query_to_show = query
            token = self.get_token(query).split()[0].strip().upper()

            if token in ['UNLOAD', 'COPY']:
                qs = query_to_show.split()
                credentials = qs[qs.index('CREDENTIALS') + 1]
                if credentials != "'None'":
                    qs[qs.index('CREDENTIALS') + 1] = "'**********************'"
                    query_to_show = ' '.join(qs)

            self._logger.debug('COMMAND = {}'.format(query_to_show.replace('\n', ' ')))

            self._cursor.execute(query)
            rc = 0
            data = list()

            if token in ['UNLOAD', 'COPY']:
                count = 'SELECT pg_last_{}_count();'.format(token)
                self._cursor.execute(count)
                rc = self._cursor.fetchone()[0]

            if token in ['UPDATE', 'DELETE', 'INSERT', 'SELECT', 'WITH']:
                rc = self._cursor.rowcount
                if token in ['SELECT', 'WITH', 'ALTER']:
                    try:
                        data = self._cursor.fetchall()
                    except Exception:
                        table = get_table_from_query(query)
                        if table:
                            count = 'SELECT count(1) FROM {};'.format(table)
                            if token == 'SELECT':
                                token = 'SELECT INTO'

                            self._cursor.execute(count)
                            rc = self._cursor.fetchone()[0]
                        pass

            item = {'token': token, 'rowcount': rc, 'data': data}
            self._logger.debug('{} {}'.format(item['token'].upper(), item['rowcount']))

            return item
        except Exception as ex:
            self._logger.error(repr(ex))
            exit(1)
            raise

    def parse_query(self, query):
        """
        Parse queries of a multiple queries string
        :param query: query with multiples queries [String]
        :return: List of queries parsed [List<String>]
        """
        try:
            l_query = list()
            query = sqlparse.format(query, strip_comments=True)
            query_splitted = sqlparse.parse(query, encoding="UTF-8")

            for st in query_splitted:
                token = str(st.token_first())
                if not ("--" in token or "/*" in token or token == "None"):
                    l_query.append(str(st))
            return l_query
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_token(self, query):
        """
        Get token for one specific query
        :param query: query script [String]
        :return: Token [String]
        """
        try:
            query = sqlparse.format(query, strip_comments=True)
            query_splitted = sqlparse.parse(query, encoding="UTF-8")

            for st in query_splitted:
                token = str(st.token_first())
                if not ("--" in token or "/*" in token or token == "None"):
                    self._logger.debug('TOKEN: {}'.format(str(token).upper()))
                    return str(token).upper()
        except Exception as ex:
            self._logger.error(repr(ex))
            raise


class Redshift(object):
    def __init__(self, host, user, password, database, port, connect_timeout=20,
                 cursor_factory=NamedTupleCursor, s3profile=None, autocommit=True, level='INFO'):
        """
        Constructor
        :param host: Host [String]
        :param user: User [String]
        :param password: Password [String]
        :param database: Database name to connect [String]
        :param port: Port number [Integer]
        :param connect_timeout: Timeout in seconds [Integer]
        :param cursor_factory: Type of cursor, DictCursor or NamedTupleCursor (Default) [Cursor]
        :param level: logging level [String]
        """
        self._logger = Logger(logger_name=__name__ + '.redshift', level=level)
        settings = {"host": host,
                    "user": user,
                    "password": password,
                    "database": database,
                    "port": port,
                    "connect_timeout": connect_timeout}

        self._settings = settings
        self._autocommit = autocommit
        self._connection = self._connect()
        self._cursor_factory = cursor_factory
        self._cursor = self._get_cursor(self._cursor_factory)
        self._s3profile = s3profile

        self._credentials = None
        if self._s3profile:
            self._credentials = self._get_profile_credentials()

    def _connect(self):
        """
        Connect to Redshift
        :return: Connection object [Connection]
        """
        try:
            conn = psycopg2.connect(**self._settings)
            conn.autocommit = self._autocommit
            return conn
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def set_autocommit(self, autocommit):
        """
        Set connection autocommit mode
        :param autocommit: True or False [Boolean]
        :return: None
        """
        try:
            self._logger.warning('Setting up autocommit mode to {autocommit}...'.format(autocommit=autocommit))
            self._autocommit = autocommit
            self._connection.autocommit = self._autocommit
            self._cursor = self._get_cursor(self._cursor_factory)
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def _get_cursor(self, cursor_factory):
        """
        Get a cursor
        :param cursor_factory: Type of cursor, NamedTupleCursor or DictCursor [CursorType]
        :return: Cursor [Cursor]
        """
        try:
            cursor = self._connection.cursor(cursor_factory=cursor_factory)
            return cursor
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def commit(self):
        """
        Commit transactions
        :return: None
        """
        try:
            if self._autocommit:
                self._logger.warning('Autocommit option is enabled. Skipping commit.')
            else:
                self._connection.commit()
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def close(self):
        """
        Close connection
        :return: None
        """
        try:
            self._connection.close()
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_settings(self, key):
        """
        Get settings by key
        :param key: key [String]
        :return: Value corresponding to the key provided [String, List, Dictionary]
        """
        value = None
        if key in self._settings and key != 'password':
            value = self._settings[key]
        return value

    def _get_profile_credentials(self):
        """
        Return credentials corresponding with the profile provided
        :return: Credentials [String]
        """
        credentials = None
        home = os.path.expanduser('~')
        aws_folder = os.path.join(home, '.aws')
        if os.path.isdir(aws_folder):
            path_aws_credentials = os.path.join(aws_folder, 'credentials')

            if os.path.isfile(path_aws_credentials):
                config_aws = ConfigFile()
                config_aws.load(path_aws_credentials)

                keys = config_aws.get(self._s3profile)

                if len(keys) == 2:
                    keys_formatted = ['{}={}'.format(k, v) for k, v in keys.items()]
                    credentials = ';'.join(keys_formatted)

        return credentials

    def set_credentials(self, credentials):
        """
        Set credentials for Redshift Unload/Copy commands
        :param credentials: Credentials [String]
        :return: None
        """
        self._credentials = credentials

    def copy(self, prefix=None, table=None, maxerror=0, truncatecolumns=False,
             emptyasnull=False, blanksasnull=False, compression=None,
             manifest=False, jsonas=None, delimiter=None, removequotes=False, acceptinvchars=False, acceptanydate=False,
             statupdate=True, compupdate=True):
        """
        Copy from S3 to Redshift
        :param prefix: S3 prefix to load, can be a manifest [String]
        :param table: Redshift table with schema [String]
        :param maxerror: Max number of errors allowed. Default: 0, Max Number: 10000 [Integer]
        :param truncatecolumns: Truncate columns values [Boolean]
        :param emptyasnull: Replace empty values with NULL [Boolean]
        :param blanksasnull: Replace blank values with NULL [Boolean]
        :param compression: Indicate if the keys to load are compressed or not, could be BZIP2 or GZIP [String]
        :param manifest: If prefix provided is a manifest [Boolean]
        :param jsonas: Auto or path to json manifest [Spring]
        :param delimiter: Delimiter of columns used in the files to load [String]
        :param removequotes: Remove quotes [Boolean]
        :param compupdate: Controls whether compression encodings are automatically applied during a COPY [Boolean]
        :param statupdate: Governs automatic computation and refresh of optimizer statistics at the end of a successful COPY command [Boolean]
        :param acceptanydate: Allows any date format [Boolean]
        :param acceptinvchars: Enables loading of data into VARCHAR columns even if the data contains invalid UTF-8 characters [Boolean]
        :return: Data, Token and Rows affected [Dictionary]
        """
        try:
            if not prefix:
                raise Exception("S3 path '{}' is not valid".format(prefix))

            if not table:
                raise Exception("Table '{}' is not valid".format(table))

            if not self._credentials:
                raise Exception('Credentials are not valid. Set the credentials')

            # Command pattern
            cmd = """
                    COPY {table}
                    FROM '{prefix}'
                    {jsonas_option}
                    {compression_option}
                    {acceptinvchars_option}
                    {acceptanydate_option} 
                    CREDENTIALS '{credentials}'
                    {manifest_option}
                    {maxerror}
                    {delimiter_option}
                    {removequotes_option}
                    {emptyasnull_option}
                    {blanksasnull_option}
                    {truncatecolumns_option}
                    {statupdate_option}
                    {compupdate_option}
                    ;
                  """
            # JSON
            jsonas_option = ''
            if jsonas:
                jsonas_option = "JSON as '{}'".format(jsonas)

            # Compression
            compression_option = ''
            if compression:
                if compression.upper() in ['BZIP2', 'LZOP', 'GZIP']:
                    compression_option = compression.upper()

            # Accept Invalid Chars
            acceptinvchars_option = ''
            if acceptinvchars:
                acceptinvchars_option = 'ACCEPTINVCHARS'

            # Accept Any Date format
            acceptanydate_option = ''
            if acceptanydate:
                acceptanydate_option = 'ACCEPTANYDATE'

            # Truncate Columns
            truncatecolumns_option = ''
            if truncatecolumns:
                truncatecolumns_option = 'TRUNCATECOLUMNS'

            # Empty as NULL
            emptyasnull_option = ''
            if emptyasnull:
                emptyasnull_option = 'EMPTYASNULL'

            # Blank as NULL
            blanksasnull_option = ''
            if blanksasnull:
                blanksasnull_option = 'BLANKASNULL'

            # Empty as NULL
            removequotes_option = ''
            if removequotes:
                removequotes_option = 'REMOVEQUOTES'

            # Manifest
            manifest_option = ''
            if manifest:
                manifest_option = 'MANIFEST'

            # Delimiter
            delimiter_option = ''
            if delimiter:
                delimiter_option = "DELIMITER '{}'".format(delimiter)

            # Compression Update
            compupdate_option = 'COMPUPDATE TRUE'
            if not compupdate:
                compupdate_option = 'COMPUPDATE FALSE'

            # Statistics Update
            statupdate_option = 'STATUPDATE TRUE'
            if not statupdate:
                statupdate_option = 'STATUPDATE FALSE'

            # Formatting copy command
            cmd = cmd.format(table=table,
                             prefix=prefix,
                             jsonas_option=jsonas_option,
                             acceptinvchars_option=acceptinvchars_option,
                             acceptanydate_option=acceptanydate_option,
                             compression_option=compression_option,
                             credentials=self._credentials,
                             manifest_option=manifest_option,
                             maxerror='MAXERROR ' + str(maxerror),
                             delimiter_option=delimiter_option,
                             removequotes_option=removequotes_option,
                             emptyasnull_option=emptyasnull_option,
                             blanksasnull_option=blanksasnull_option,
                             truncatecolumns_option=truncatecolumns_option,
                             compupdate_option=compupdate_option,
                             statupdate_option=statupdate_option)

            cmd = os.linesep.join([s.strip() for s in cmd.splitlines() if s.strip()])
            return self.execute(cmd)
        except Exception as ex:
            raise

    def unload(self, prefix, query, compression=None, allowoverwrite=True,
               delimiter=None, escape=True, addquotes=False, parallel=True,
               nullas=None, maxfilesize_in_mb=None):
        """
        Unload data from Redshift
        :param prefix: S3 prefix in which the data will be unloaded [String]
        :param query: Query with logic to unload [String]
        :param compression: BZIP2 or GZIP, in case that you want to unload data compressed [String]
        :param allowoverwrite: Overwrite files in S3 or not. Default: False [Boolean]
        :param delimiter: Delimiter used to separate columns [String]
        :param escape: If the file contains special characters, must be escaped. Default: False [Boolean]
        :param addquotes: Add quotes. Default: False [Boolean]
        :param parallel: Activate or deactivate parallel unload. Default: True [Boolean]
        :param nullas: Value to replace NULL values [String]
        :param maxfilesize_in_mb: Max file size in MB for each file generated [Integer]
        :return: Data, Token and Rows affected [Dictionary]
        """
        try:
            if not prefix:
                raise Exception("S3 path '{}' is not valid".format(prefix))

            if not query:
                raise Exception('Query provided is not valid')

            # Command pattern
            cmd = """
                    UNLOAD ('{query}')
                    TO '{prefix}'
                    CREDENTIALS '{credentials}'
                    {compression_option}
                    {delimiter_option}
                    {escape_option}
                    {addquotes_option}
                    {nullas_option}
                    {allowoverwrite_option}
                    {parallel_option}
                    {maxfilesize_option}
                    ;
                  """

            # Compression
            compression_option = ''
            if compression:
                if compression.upper() in ['BZIP2', 'LZOP', 'GZIP']:
                    compression_option = compression.upper()

            # Delimiter
            delimiter_option = ''
            if delimiter:
                delimiter_option = "DELIMITER '{}'".format(delimiter)

            # Escape option
            escape_option = ''
            if escape:
                escape_option = 'ESCAPE'

            # Addquotes option
            addquotes_option = ''
            if addquotes:
                addquotes_option = 'ADDQUOTES'

            # NULL as option
            nullas_option = ''
            if nullas:
                nullas_option = "NULL AS '{}'".format(nullas)

            # Allow overwrite option
            allowoverwrite_option = ''
            if allowoverwrite:
                allowoverwrite_option = 'ALLOWOVERWRITE'

            # Parallel option
            parallel_option = 'PARALLEL TRUE'
            if not parallel:
                parallel_option = 'PARALLEL FALSE'

            # Max file size option
            maxfilesize_option = ''
            if maxfilesize_in_mb:
                maxfilesize_option = 'MAXFILESIZE AS {} MB'.format(maxfilesize_in_mb)

            # Formatting unload command
            cmd = cmd.format(query=query,
                             prefix=prefix,
                             credentials=self._credentials,
                             compression_option=compression_option,
                             delimiter_option=delimiter_option,
                             escape_option=escape_option,
                             addquotes_option=addquotes_option,
                             nullas_option=nullas_option,
                             allowoverwrite_option=allowoverwrite_option,
                             parallel_option=parallel_option,
                             maxfilesize_option=maxfilesize_option)

            cmd = os.linesep.join([s.strip() for s in cmd.splitlines() if s.strip()])
            return self.execute(cmd)
        except Exception as ex:
            raise

    def insert(self, into_table=None, from_table=None, **kwargs):
        """
        Generate INSERT statement
        :param into_table: Target table name with schema [String]
        :param from_table: From table name with schema [String]
        :param kwargs: Fields mapping between target and from table, or mapping between columns and values [Dictionary]
        :return: Data, Token and Rows affected [Dictionary]
        """
        try:
            if not into_table:
                raise Exception('Missing target table')

            # Listing values and fields
            l_values = list()
            l_fields = list()

            if len(kwargs) == 0:
                cmd = 'INSERT INTO {into_table} '
                l_values.append('*')
            else:
                cmd = 'INSERT INTO {into_table} ({into_fields}) '
                for arg in kwargs:
                    l_fields.append(arg)
                    value = str(kwargs[arg])
                    if not from_table:
                        try:
                            long(value)
                        except Exception:
                            try:
                                float(value)
                            except Exception:
                                value = "'{}'".format(value)
                                pass
                            pass
                        l_values.append(value)
                    else:
                        l_values.append(kwargs[arg])

            if from_table:
                cmd += 'SELECT {from_fields} FROM {from_table};'
            else:
                cmd += 'VALUES ({from_fields});'

            into_fields = ', '.join(l_fields)
            from_fields = ', '.join(l_values)

            cmd = cmd.format(into_table=into_table, into_fields=into_fields,
                             from_fields=from_fields, from_table=from_table)

            return self.execute(cmd)
        except Exception as ex:
            raise

    def drop(self, table, table_type='table', cascade=True):
        """
        Drop Redshift table
        :param table: Table name with schema [String]
        :param table_type: view or table [String]
        :param cascade: enable cascade mode [Boolean]
        :return: Data, Token and Rows affected [Dictionary]
        """
        cmd = 'DROP TABLE IF EXISTS {}'.format(table)
        if table_type == 'view':
            cmd = 'DROP VIEW IF EXISTS {}'.format(table)

        if cascade:
            cmd += ' CASCADE;'
        else:
            cmd += ';'

        return self.execute(cmd)

    def truncate(self, table):
        """
        Truncate Redshift table
        :param table: Table name with schema [String]
        :return: Data, Token and Rows affected [Dictionary]
        """
        cmd = "TRUNCATE {};".format(table)
        return self.execute(cmd)

    def analyze(self, table):
        """
        Analyze Redshift table
        :param table: Table name with schema [String]
        :return: Data, Token and Rows affected [Dictionary]
        """
        cmd = "ANALYZE {};".format(table)
        return self.execute(cmd)

    def vacuum(self, table):
        """
        Vacuum Redshift table
        :param table: Table name with schema [String]
        :return: Data, Token and Rows affected [Dictionary]
        """
        cmd = "VACUUM {};".format(table)
        return self.execute(cmd)

    def get_columns_name(self, table, schema=None):
        """
        Get columns name for a given table
        :param table: Table name [String]
        :param schema: Schema name. None value for temp tables [String]
        :return: List of columns name [List<String>]S
        """
        query = """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = '{}'
                    AND table_schema LIKE '{}'
                    ORDER BY ordinal_position;
                """

        if schema:
            schema = '%{}%'.format(schema)
        else:
            schema = '%_temp_%'

        query = query.format(table, schema)
        result = self.execute(query.format(table, schema))

        l_columns = list()
        for row in result['data']:
            l_columns.append(row.column_name)
        return l_columns

    def get_partitions(self, schema=None, table=None):
        if schema and table:
            query = """
                        SELECT
                          schemaname || '.' || tablename    AS table,
                          location                          AS partition
                        FROM SVV_EXTERNAL_PARTITIONS
                        WHERE schemaname = '{}'
                        AND   tablename  = '{}'
                        ;
                    """.format(schema, table)
        else:
            query = """
                        SELECT
                          schemaname || '.' || tablename    AS table,
                          location                          AS partition
                        FROM SVV_EXTERNAL_PARTITIONS
                        ;
                    """
        result = self.execute(query)

        l_tables = list()
        for row in result['data']:
            l_tables.append({"table": row.table, "partition": row.partition})
        return l_tables

    def get_external_tables(self, schema=None, table=None):
        if schema and table:
            query = """
                        SELECT
                          schemaname || '.' || tablename    AS table,
                          location,
                          input_format,
                          output_format,
                          serialization_lib,
                          serde_parameters,
                          compressed
                        FROM SVV_EXTERNAL_TABLES
                        WHERE schemaname = '{}'
                        AND   tablename  = '{}'
                        ;
                    """.format(schema, table)
        else:
            query = """
                        SELECT
                          schemaname || '.' || tablename    AS table,
                          location,
                          input_format,
                          output_format,
                          serialization_lib,
                          serde_parameters,
                          compressed
                        FROM SVV_EXTERNAL_TABLES
                        ;
                    """
        result = self.execute(query)

        l_tables = list()
        for row in result['data']:
            l_tables.append({"table": row.table,
                             "location": row.location,
                             "input_format": row.input_format,
                             "output_format": row.output_format,
                             "serialization_lib": row.serialization_lib,
                             "serde_params": json.loads(row.serde_parameters),
                             "compressed": row.compressed})

            return l_tables

    def is_external(self, schema, table):
        return (schema + '.' + table) in [t["table"] for t in self.get_external_tables()]

    def add_partition(self, schema, table, partitions, with_partition_name=True):
        rc = 0
        result = self.get_external_tables(schema, table)

        if len(result) == 1:
            l_partitions = list()
            l_values = list()

            for k, v in partitions.iteritems():
                l_partitions.append("{}={}".format(k, v))
                if with_partition_name:
                    l_values = l_partitions
                else:
                    l_values.append(v)

            partition = '/'.join([result[0]["location"]] + l_values)
            query = """
                        ALTER TABLE {}.{} 
                        ADD IF NOT EXISTS PARTITION({}) 
                        LOCATION '{}'
                        ;
                    """.format(schema, table, ','.join(l_partitions), partition)

            rc = self.execute(query)['rowcount']
            if rc == 1:
                self._logger.info("Added partition [{}] to the table {}.{}".format(','.join(l_partitions), schema, table))
            else:
                self._logger.warning("Partition [{}] could not be added to the table {}.{}".format(','.join(l_partitions), schema, table))

        else:
            self._logger.warning("Table {} is not an external table mapped in Redshift".format(schema + '.' + table))

        return rc

    def get_ddl(self, schema, table, is_external=False, replace_table_name=None):
        ddl = ""
        if not replace_table_name:
            replace_table_name = table

        if is_external:
            query = """
                        SELECT
                            columnname      AS column,
                            external_type   AS datatype,
                            part_key        AS partition_key
                        FROM SVV_EXTERNAL_COLUMNS
                        WHERE schemaname = '{}'
                        AND   tablename = '}'
                        ORDER BY columnnum, part_key
                    ;                   
                    """.format(schema, table)
            result = self.execute(query)

            if len(result['data']) > 0:
                l_colums = list()
                l_partitions = list()
                for row in result['data']:
                    if row.partition_key != 0:
                        l_partitions.append({"column": row.column, "type": row.datatype})
                    else:
                        l_colums.append({"column": row.column, "type": row.datatype})

                table_info = self.get_external_tables(schema, table)

                l_columns_ddl = list()
                l_partitions_ddl = list()
                for c in l_colums:
                    l_columns_ddl.append("{} {}".format(c["column"], c["type"]))

                for c in l_partitions:
                    l_partitions_ddl.append("{} {}".format(c["column"], c["type"]))

                ddl = """
                        CREATE EXTERNAL TABLE {}.{} ({})
                        PARTITIONED BY ({})
                        ROW FORMAT SERDE '{}'
                        STORED AS INPUTFORMAT '{}'
                        OUTPUTFORMAT '{}'
                        LOCATION '{}'
                        ;
                      """.format(schema,
                                 replace_table_name,
                                 ','.join(l_columns_ddl),
                                 ','.join(l_partitions_ddl),
                                 table_info[0]["serialization_lib"],
                                 table_info[0]["input_format"],
                                 table_info[0]["output_format"],
                                 table_info[0]["location"])

        else:
            #@TODO: add ddl calculation for non external tables (normal tables)
            # query = ""
            ddl = ""

        return ddl

    def execute(self, query):
        """
        Execute simple query
        :param query: query script [String]
        :return: Data, Token and Rows affected [Dictionary]
        """
        def get_table_from_query(script):
            index = 0
            tablename = None
            lines = script.split()
            while index < len(lines):
                if lines[index] in ('INTO', 'APPEND'):
                    if lines[index + 1].upper() == 'TEMP':
                        tablename = lines[index + 2].replace(';', '')
                    elif lines[index + 1].upper() == 'FROM':
                        tablename = lines[index + 2].replace(';', '')
                    else:
                        tablename = lines[index + 1].replace(';', '')
                    index = len(lines)
                else:
                    index += 1
            return tablename

        try:
            query = query.strip()
            query_to_show = query
            token = self.get_token(query).split()[0].strip().upper()

            if token in ['UNLOAD', 'COPY']:
                qs = query_to_show.split()
                credentials = qs[qs.index('CREDENTIALS') + 1]
                if credentials != "'None'":
                    qs[qs.index('CREDENTIALS') + 1] = "'**********************'"
                    query_to_show = ' '.join(qs)

            self._logger.debug('COMMAND = {}'.format(query_to_show.replace('\n', ' ')))

            self._cursor.execute(query)
            rc = 0
            data = list()

            if token == 'ALTER' and ("ADD PARTITION" in query or "ADD IF NOT EXISTS PARTITION" in query):
                tablename = query[query.find('TABLE') + 5:query.find('ADD')].strip()
                schema = tablename.split('.')[0]
                table = tablename.split('.')[1]
                partition = query[query.find('LOCATION') + 8:-1].strip()[1:-1]

                if partition in [t["partition"] for t in self.get_partitions(schema, table)]:
                    rc = 1

            if token in ['UNLOAD', 'COPY']:
                count = 'SELECT pg_last_{}_count();'.format(token)
                self._cursor.execute(count)
                rc = self._cursor.fetchone()[0]

            if token in ['UPDATE', 'DELETE', 'INSERT', 'SELECT', 'WITH']:
                rc = self._cursor.rowcount
                if token in ['SELECT', 'WITH', 'ALTER']:
                    try:
                        data = self._cursor.fetchall()
                    except Exception:
                        table = get_table_from_query(query)
                        if table:
                            count = 'SELECT count(1) FROM {};'.format(table)
                            if token == 'SELECT':
                                token = 'SELECT INTO'

                            self._cursor.execute(count)
                            rc = self._cursor.fetchone()[0]
                        pass

            item = {'token': token, 'query': query, 'rowcount': rc, 'data': data}
            self._logger.debug('{} {}'.format(item['token'].upper(), item['rowcount']))

            return item
        except psycopg2.InternalError as ie:
            lower_limit = ie.message.find("error") + 6
            upper_limit = ie.message[lower_limit:].find('\n')
            msg = ie.message[lower_limit:lower_limit + upper_limit].strip()

            self._logger.error(msg)
            raise psycopg2.InternalError(msg)
        except psycopg2.ProgrammingError as pe:
            self._logger.error(pe.message)
            raise
        except psycopg2.DataError as dd:
            self._logger.error(dd.message)
            raise
        except psycopg2.DatabaseError as de:
            self._logger.error(de.message)
            raise

    def parse_query(self, query):
        """
        Parse queries of a multiple queries string
        :param query: query with multiples queries [String]
        :return: List of queries parsed [List<String>]
        """
        try:
            l_query = list()
            query = sqlparse.format(query, strip_comments=True)
            query_splitted = sqlparse.parse(query, encoding="UTF-8")

            for st in query_splitted:
                token = str(st.token_first())
                if not ("--" in token or "/*" in token or token == "None"):
                    l_query.append(str(st))
            return l_query
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_token(self, query):
        """
        Get token for one specific query
        :param query: query script [String]
        :return: Token [String]
        """
        try:
            query = sqlparse.format(query, strip_comments=True)
            query_splitted = sqlparse.parse(query, encoding="UTF-8")

            for st in query_splitted:
                token = str(st.token_first())
                if not ("--" in token or "/*" in token or token == "None"):
                    self._logger.debug('TOKEN: {}'.format(str(token).upper()))
                    return str(token).upper()
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def change_owner(self, table, user=None):
        """
        Truncate Redshift table
        :param table: Table name with schema [String]
        :param user: DB user that will become the new owner of table [String]
        :return: None or name of the old owner [String]
        """
        d_owners = {'new': None, 'old': None}
        if not user:
            user = self.get_settings(key='user')

        # Table
        table = table.lower()
        schemaname = table.split('.')[0]
        tablename = table.split('.')[1]

        # Get current owner of the table
        q_owner = """
                    SELECT
                      tableowner  AS owner
                    FROM pg_tables
                    WHERE schemaname = '{schemaname}'
                    AND   tablename  = '{tablename}';
                  """.format(schemaname=schemaname, tablename=tablename)

        q_owner_result = self.execute(q_owner)

        if len(q_owner_result['data']) > 0:
            current_owner = q_owner_result['data'][0].owner
            self._logger.debug('The owner of the table {table} is {owner}'.format(table=table, owner=current_owner))

            q_alter_owner = 'ALTER TABLE {table} OWNER TO {owner};'.format(table=table, owner=user)
            self.execute(q_alter_owner)

            self._logger.info('Owner of the table {table} has been changed to {user}'.format(table=table, user=user))
            d_owners['old'] = current_owner
            d_owners['new'] = user

        else:
            self._logger.warning('The table {table} was not found in the DB'.format(table=table))

        return d_owners


class Athena(object):
    def __init__(self, profile=None, database=None, output=None, level='INFO'):
        """
        Constructor
        :param profile: AWS profile to get credentials from local configuration
        :param database: database name [String]
        :param output: S3 path (format s3://<bucket>/<prefix>) used for query output [String]
        :param level: logging level [String]
        """
        self._logger = Logger(logger_name=__name__ + '.athena', level=level)
        self._profile = profile
        self._database = None
        self._output = None

        self.set_database(database)
        self.set_output(output)

        try:
            self.session = boto3.Session(profile_name=self._profile)
            self.client = self.session.client('athena')

            self._logger.debug('S3 PROFILE = {}'.format(self._profile))
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def set_database(self, database):
        """
        Set database
        :param database: database name
        :return: None
        """
        self._database = database or 'panamera_data_lake'

    def set_output(self, output):
        """
        Set output prefix
        :param output: S3 path (format s3://<bucket>/<prefix>) used for query output [String]
        :return: None
        """
        date = datetime.now()
        self._output = output or 's3://aws-athena-query-results-657245296933-us-west-2/tmp/'

    def refresh_partitions(self, table):
        """
        Update partitions for an specific table
        :param table: table name in the catalog [String]
        :return: query identifier [String]
        """
        query = 'MSCK REPAIR TABLE {db}.{table};'.format(db=self._database, table=table)

        return self.execute_query(query)

    def execute_query(self, query):
        """
        Execute Athena query
        :param query: query command to run [String]
        :return: query identifier [String]
        """
        date = datetime.now()
        output = self._output + 'Unsaved/{year}/{month}/{day}/'.format(year=str(date.now().year),
                                                                       month=str(date.month).zfill(2),
                                                                       day=str(date.day).zfill(2))
        args = {
                'QueryString': '{query}'.format(query=query),
                'ResultConfiguration': {'OutputLocation': '{output}'.format(output=output)},
                'QueryExecutionContext': {'Database': self._database}
                }

        try:
            result = self.client.start_query_execution(**args)
            return result['QueryExecutionId']
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_status(self, query_id):
        """
        Get current status of query in Athena
        :param query_id: query identifier in Athena [String]
        :return: status of query [Dictionary]
        """
        try:
            return self.client.get_query_execution(QueryExecutionId=query_id)
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_results(self, query_id, next_token=None, max_results=1000):
        """
        Get query results
        :param query_id: query identifier in Athena [String]
        :param next_token: the token that specifies where to start pagination if a previous request was truncated [String]
        :param max_results: the maximum number of results (rows) to return in this request [Integer]
        :return: query results [Dictionary]
        """
        result = None
        sts = self.get_status(query_id)

        if sts['QueryExecution']['Status']['State'] != 'RUNNING':
            args = {
                    'QueryExecutionId': query_id,
                    'MaxResults': max_results
                   }

            if next_token:
                args['NextToken'] = next_token

            result = self.client.get_query_results(**args)

        return result

    def get_result_count(self, query_id):
        """
        Get size of resultset
        :param query_id: query identifier in Athena [String]
        :return: resultset size [Integer]
        """
        # @TODO: implement count when the output is paginated
        count = 0
        try:
            more_data = True
            result = self.get_results(query_id)

            while more_data:
                if 'NextToken' in result:
                    count += len(result['ResultSet']['Rows'])
                    result = self.get_results(query_id=query_id, next_token=result['NextToken'])
                else:
                    count += len(result['ResultSet']['Rows']) - 1
                    more_data = False

        except Exception as ex:
            self._logger.error(repr(ex))
            pass

        return count

    def __repr__(self):
        return str({'Resource': 'Athena', 'Profile': self._profile, 'Database': self._database, 'Output': self._output})


class S3(object):
    def __init__(self, bucket, profile=None, arn=None, level='INFO'):
        """
        Constructor
        :param bucket: Bucket name [String]
        :param profile: AWS profile to get credentials from local configuration
        :param arn: ARN role to assume [String]
        :param level: logging level [String]
        """
        self._logger = Logger(logger_name=__name__ + '.s3', level=level)
        self.profile = profile
        self.arn = arn
        self.bucket_name = bucket
        try:
            if arn:
                self.sts_client = boto3.client('sts')
                assumed_role = self.sts_client.assume_role(
                    RoleArn=self.arn,
                    RoleSessionName="s3-{}-session".format(self.bucket_name)
                )

                credentials = assumed_role['Credentials']
                self.session = boto3.Session(
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken']
                )
            else:
                self.session = boto3.Session(profile_name=self.profile)

            self.resource = self.session.resource('s3')
            self.client = self.session.client('s3')
            self.bucket = self.resource.Bucket(self.bucket_name)

            self._logger.debug('BUCKET NAME = {}'.format(self.bucket_name))
            self._logger.debug('S3 PROFILE = {}'.format(self.profile))
            self._logger.debug('ARN = {}'.format(self.arn))

        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_credentials_keys(self):
        """
        Get access and secret key associated to this session
        :return: access and secret key [Dictionary]
        """
        return self.session.get_credentials()

    def _filter_objects(self, prefix, filter=None, recursive=False):
        """
        Get objects filtered from S3
        :param prefix: S3 prefix [String]
        :param filter: Regular expression for filtering prefix [String]
        :param recursive: Just in case you need to get all keys included in all prefixes [Boolean]
        :return: Item from S3 [Dictionary]
        """
        try:
            # Regular expression
            regex = None
            if filter:
                regex = re.compile(filter)

            # Arguments
            args = dict()
            args['Bucket'] = self.bucket_name
            args['Prefix'] = prefix

            if not recursive:
                args['Delimiter'] = '/'

            # Paginator
            paginator = self.client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(**args)

            if recursive:
                for page in page_iterator:
                    if 'Contents' in page:
                        for e in page['Contents']:
                            if regex:
                                if not re.search(regex, e['Key']):
                                    break
                                else:
                                    elem = {'Key': e['Key'], 'LastModified': e['LastModified'], 'Size': e['Size']}
                            else:
                                elem = {'Key': e['Key'], 'LastModified': e['LastModified'], 'Size': e['Size']}

                            self._logger.debug('S3 OBJECT = {}'.format(elem))
                            yield elem
            else:
                for page in page_iterator:
                    if 'CommonPrefixes' in page:
                        for e in page['CommonPrefixes']:
                            if regex:
                                if not re.search(regex, e['Prefix']):
                                    break
                                else:
                                    elem = {'Key': e['Prefix'], 'LastModified': None, 'Size': 0}
                            else:
                                elem = {'Key': e['Prefix'], 'LastModified': None, 'Size': 0}

                            self._logger.debug('S3 OBJECT = {}'.format(elem))
                            yield elem

        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def generate_url(self, key, expires_in=3600):
        try:
            url = self.client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in,
                HttpMethod='GET'
            )
            return url
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def upload(self, local_path, prefix):
        """
        Upload file from local machine to S3
        :param local_path: Absolute path of local directory with files to be uploaded, or absolute path of an specific
                           file to upload [String]
        :param prefix: S3 prefix in which the file/s must be uploaded [String]
        :return: List of all keys uploaded [List<String>]
        """
        try:
            # Formatting prefix
            sep = '/'
            prefix = sep.join([x for x in prefix.split(sep) if x.strip()])

            # Building list of local files to process
            if os.path.isdir(local_path):
                local_files = [os.path.join(root, name) for root, dirs, files in os.walk(local_path) for name in files]
            else:
                local_files = [local_path]

            # Uploading files to S3
            l_uploaded_objects = list()
            for file in local_files:
                filename = file.split(os.sep)[-1]
                key = '/'.join([prefix, filename])
                self.resource.Object(self.bucket_name, key).upload_file(file)
                l_uploaded_objects.append(key)

            return l_uploaded_objects
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def download(self, prefix, local_path):
        """
        Download S3 objects with the same prefix to local directory
        :param prefix: S3 prefix or key [String]
        :param local_path: Absolute path of local directory in which the files must be saved [String]
        :return: List with all paths to local files saved [List<String>]
        """
        try:
            l_downloaded_objects = list()
            if os.path.isfile(local_path):
                raise Exception('Local path provided is a file, not a directory')

            # Create directory if does not exist
            if not os.path.exists(local_path):
                os.mkdir(local_path)

            for obj in self.bucket.objects.filter(Prefix=prefix):
                filename = obj.key.split('/')[-1]

                # Replace the prefix
                file = os.path.join(local_path, filename)
                self.resource.Object(obj.bucket_name, obj.key).download_file(file)
                l_downloaded_objects.append(file)

            return l_downloaded_objects

        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def remove(self, prefix):
        """
        Remove S3 objects with the same prefix
        :param prefix: S3 prefix or key [String]
        :return: List with all S3 keys removed [List<String>]
        """
        try:
            l_removed_objects = list()
            for obj in self.bucket.objects.filter(Prefix=prefix):
                obj.delete()
                l_removed_objects.append(obj.key)
            return l_removed_objects

        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def copy(self, source_prefix, destination_prefix, destination_bucket_name=None, destination_profile=None,
             delete_source_key=False):
        """
        Copy keys from one bucket to another one.
        :param source_prefix: Source S3 prefix or key [String]
        :param destination_prefix: Destination S3 prefix or key [String]
        :param destination_bucket_name: Destination bucket name. If it's None, source and destination buckets will be
                                        the same [String]
        :param destination_profile: AWS profile to have permissions in destination bucket [String]
        :param delete_source_key: Flag to indicate if the key of the source bucket should be removed once the copy
                                  is complete [Boolean]
        :return: List with all S3 keys copied [List<String>]
        """
        try:
            # Formatting prefix
            sep = '/'
            source_prefix = sep.join([x for x in source_prefix.split(sep) if x.strip()])
            destination_prefix = sep.join([x for x in destination_prefix.split(sep) if x.strip()])

            if not destination_profile:
                destination_profile = self.profile

            if not destination_bucket_name:
                destination_bucket_name = self.bucket_name

            if destination_profile == self.profile and destination_bucket_name == self.bucket_name:
                destination_bucket = self.bucket
            else:
                session = boto3.Session(profile_name=destination_profile)
                resource = session.resource('s3')
                destination_bucket = resource.Bucket(destination_bucket_name)

            l_copied_objects = list()
            for obj in self.bucket.objects.filter(Prefix=source_prefix):
                source_object = {'Bucket': obj.bucket_name,
                                 'Key': obj.key}

                # Replace the prefix
                suffix = obj.key.replace(source_prefix, destination_prefix)

                destination_key = sep.join([x for x in suffix.split(sep) if x.strip()])
                destination_object = destination_bucket.Object(destination_key)

                extra_args = {
                    'ACL': 'bucket-owner-full-control'
                }

                destination_object.copy(source_object, extra_args)
                l_copied_objects.append(destination_key)

                # Remove source object
                if delete_source_key:
                    obj.delete()

            return l_copied_objects

        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def list(self, prefix, filter=None, with_size=False, with_last_modified=False, recursive=False):
        """
        Get a list with all objects with the same prefix
        :param prefix: S3 prefix [String]
        :param filter: Regular expression for filtering prefix [String]
        :param with_size: Flag to include Size property in the list returned [Long]
        :param with_last_modified: Flag to include Last Modified property in the list returned [Long]
        :param recursive: Just in case you need to get all keys included in all prefixes [Boolean]
        :return: List with all S3 objects. Keys available in each dictionary: Key, Size and/or LastModified [List<Dict>]
        """
        try:
            l_remote_objects = list()
            for obj in self._filter_objects(prefix, filter=filter, recursive=recursive):
                if not with_size:
                    del obj['Size']

                if not with_last_modified:
                    del obj['LastModified']

                l_remote_objects.append(obj)
            return l_remote_objects
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def listiter(self, prefix, filter=None, with_size=False, with_last_modified=False, recursive=False):
        """
        Get a list with all objects with the same prefix in iterable object
        :param prefix: S3 prefix [String]
        :param filter: Regular expression for filtering prefix [String]
        :param with_size: Flag to include Size property in the list returned [Long]
        :param with_last_modified: Flag to include Last Modified property in the list returned [Long]
        :param recursive: Just in case you need to get all keys included in all prefixes [Boolean]
        :return: List with all S3 objects. Keys available in each dictionary: Key, Size and/or LastModified [List<Dict>]
        """
        try:
            for obj in self._filter_objects(prefix, filter=filter, recursive=recursive):
                if not with_size:
                    del obj['Size']

                if not with_last_modified:
                    del obj['LastModified']

                yield obj
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def count(self, prefix, filter=None, recursive=False):
        """
        Get count of objects with the same prefix
        :param prefix: S3 prefix [String]
        :param filter: Regular expression for filtering prefix [String]
        :param recursive: Just in case you need to get all keys included in all prefixes [Boolean]
        :return: Count of objects [Long]
        """
        try:
            count_objects = 0
            for _ in self._filter_objects(prefix, filter=filter, recursive=recursive):
                count_objects += 1
            return count_objects
        except Exception as ex:
            print(repr(ex))
            raise

    def exists(self, prefix):
        """
        Check if the prefix exists in S3
        :param prefix: S3 prefix or key [String]
        :return: True if exists, otherwise, False [Boolean]
        """
        try:
            check = False
            if len([x for x in self._filter_objects(prefix, recursive=True)]) > 0:
                check = True

            return check
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def last_modified(self, prefix, filter=None, with_keys=False, recursive=False):

        """
        Get the max last modified date between all objects with the same prefix, including keys
        :param prefix: S3 prefix or key [String]
        :param filter: Regular expression for filtering prefix [String]
        :param with_keys: In case you need the key of the last object modified [Boolean]
        :param recursive: Just in case you need to get all keys included in all prefixes [Boolean]
        :return: Dictionary with keys LastModification and LastKeysModified (if with_keys is True)
                 [Dictionary<Datetime, List<String>]
        """
        try:
            last_modified = None
            l_last_keys_modified = list()
            for obj in self._filter_objects(prefix, filter=filter, recursive=recursive):
                tmp_last_modified = obj['LastModified']
                if (not last_modified) or (tmp_last_modified >= last_modified):
                    if not last_modified == tmp_last_modified:
                        l_last_keys_modified = list()

                    if with_keys:
                        l_last_keys_modified.append(obj['Key'])
                    last_modified = tmp_last_modified

            last_modifications = {'LastModification': last_modified}

            if with_keys:
                last_modifications['LastKeysModified'] = l_last_keys_modified

            return last_modifications
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def size(self, prefix, filter=None, recursive=False):
        """
        Get total size for all keys with the same prefix
        :param prefix:  S3 prefix or key [String]
        :param filter: Regular expression for filtering prefix [String]
        :param recursive: Just in case you need to get all keys included in all prefixes [Boolean]
        :return: Size in bytes [Long]
        """
        try:
            total_size = 0
            for obj in self._filter_objects(prefix, filter=filter, recursive=recursive):
                    total_size += obj['Size']
            return total_size
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def full_path(self, prefix, bucket_name=None):
        """
        Get S3 full path
        :param prefix: S3 prefix or key [String]
        :param bucket_name: Bucket name, in case that another bucket be required [String]
        :return: S3 full path in format s3://<bucket/<prefix> [String]

        """
        # Formatting prefix
        sep = '/'
        prefix = sep.join([x for x in prefix.split(sep) if x.strip()])

        if not bucket_name:
            bucket_name = self.bucket_name

        path = sep.join(['s3:/', bucket_name, prefix])
        self._logger.debug('S3 FULL PATH = {}'.format(path))

        return sep.join(['s3:/', bucket_name, prefix])


class Neptune(object):
    def __init__(self, endpoint, level='INFO'):
        """
        Constructor
        """


class Kinesis(object):
    def __init__(self, aws_region, stream, shard_id, last_seq=None, arn=None, min_time_lag=5, max_stream_process_time_in_sec=600, level='INFO'):
        """
        Constructor
        :param aws_region: aws region [String]
        :param stream: kinesis stream name [String]
        :param shard_id: shard identifier [String]
        :param arn: iam role to assume [String]
        :param level: logging level [String]
        """
        self._logger = Logger(logger_name=__name__ + '.kinesis', level=level)
        self._aws_region = aws_region
        self._stream = stream
        self._shard_id = shard_id
        self._arn = arn
        self._last_seq = last_seq
        self._min_time_lag = min_time_lag
        self._max_stream_process_time_in_sec = max_stream_process_time_in_sec

        if self._arn:
            response = boto3.client('sts').assume_role(RoleArn=self._arn, RoleSessionName='role')
            self._logger.info('Kinesis client assumed role: {arn}'.format(arn=self._arn))

            self._client = boto3.client('kinesis',
                                        region_name=self._aws_region,
                                        aws_access_key_id=response['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                                        aws_session_token=response['Credentials']['SessionToken'])
        else:
            self._client = boto3.client('kinesis')

    @staticmethod
    def _is_record_empty(record):
        """
        Check if record is empty
        :param record:
        :return:
        """
        try:
            json.loads(record[u'Data'])
            return False
        except ValueError:
            return True

    def set_last_sequence(self, seq):
        """
        Set last sequence read
        :param seq: sequence number [Long]
        :return: None
        """
        self._last_seq = seq

    def keys_generator(self):
        """
        Get keys from Kinesis stream
        :return: keys as iterator [Iterator]
        """
        if self._last_seq and str.isdigit(str(self._last_seq)):
            self._logger.info('Fetching data starting from the sequence number: {}'.format(self._last_seq))
            shard_iter = self._client.get_shard_iterator(
                StreamName=self._stream,
                ShardId=self._shard_id,
                ShardIteratorType='AFTER_SEQUENCE_NUMBER',
                StartingSequenceNumber=self._last_seq)

        else:
            self._logger.warning('Could not fetch the latest sequence number, will fetch from the earliest point available')

            shard_iter = self._client.get_shard_iterator(
                StreamName=self._stream,
                ShardId=self._shard_id,
                ShardIteratorType='TRIM_HORIZON')

        assert shard_iter['ResponseMetadata']['HTTPStatusCode'] == 200
        assert shard_iter['ShardIterator']

        next_shard_iterator = shard_iter['ShardIterator']
        consecutive_empty_shards = 0
        time_streaming_start = time.time()

        while True:
            shard_iterator = next_shard_iterator
            consecutive_empty_shards += 1

            try:
                records_response = self._client.get_records(ShardIterator=shard_iterator)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] != 'ProvisionedThroughputExceededException':
                    raise e
                self._logger.debug('Got ProvisionedThroughputExceededException - will sleep for 5 seconds')
                time.sleep(5)
                continue

            if records_response is None:
                self._logger.debug('ShardIterator was closed.')
                break
            else:
                self._logger.debug('Got {} records ({} minutes behind latest)'.format(len(records_response['Records']), round(records_response['MillisBehindLatest'] / (1000 * 60))))

            for record in records_response['Records']:
                if self._is_record_empty(record):
                    self._logger.debug('Empty record')
                    break

                sequence_number = record[u'SequenceNumber']
                time_arrival = record[u'ApproximateArrivalTimestamp']
                d = json.loads(record[u'Data'])

                self._logger.debug('{"SequenceNumber": {}, "ApproximateArrivalTimestamp": {}, "Data": {}}'.format(sequence_number, time_arrival, d))

                amnesia_request = False
                if 'type' in d:
                    if d['type'] == 'overwritten_by_amnesia':
                        amnesia_request = True

                self._last_seq = sequence_number

                yield dict(time_arrival=time_arrival,
                           sequence=sequence_number,
                           bucket=d['source_bucket'],
                           key=d['file_name'],
                           amnesia_request=amnesia_request)

                consecutive_empty_shards = 0

            next_shard_iterator = records_response.get('NextShardIterator', None)

            if not next_shard_iterator:
                self._logger.debug('Shutting down stream, REASON: exhaust stream shard iterator.')
                break

            timelag = round(records_response['MillisBehindLatest'] / 1000)
            self._logger.debug('Timelag {time}'.format(time=timelag))

            if timelag < self._min_time_lag:
                self._logger.debug('Shutting down stream, REASON: stream events caught up with present.')
                break
            stream_processing_time = time.time() - time_streaming_start
            self._logger.debug('Processing stream since {time}'.format(time=stream_processing_time))
            if stream_processing_time > self._max_stream_process_time_in_sec:
                self._logger.debug('Shutting down stream, REASON: reach max streaming duration.')
                break


class EMR(object):
    def __init__(self, name, aws_region, applications, logs, bootstrap, script, emr_version, subnet_id, security_group,
                 master_instance_type, master_instance_count, master_instance_volume_size, master_instance_volume_type, master_instance_volume_count,
                 slave_instance_type=None, slave_instance_count=None, slave_instance_volume_size=None, slave_instance_volume_type=None, slave_instance_volume_count=None,
                 key_name=None, arn=None, level='INFO'):
        """
        Constructor
        :param name: cluster name [String]
        :param aws_region: aws region of the cluster [String]
        :param applications: list of applications to use in the EMR cluest [List<String>]
        :param logs: S3 prefix to store the logs [String]
        :param bootstrap: remote local path to bootstrap file [String]
        :param script: remote local path to script to run [String]
        :param emr_version: emr version [String]
        :param subnet_id: subnet identifier [String]
        :param security_group: security group [String]
        :param master_instance_type: master instance type [String]
        :param master_instance_count: number of master instances [Integer]
        :param master_instance_volume_size: volume size in GB [Integer]
        :param master_instance_volume_type: volume type [Integer]
        :param master_instance_volume_count: volume count [Integer]
        :param slave_instance_type: slave instance type [String]
        :param slave_instance_count: number of slave instances [Integer]
        :param slave_instance_volume_size: volume size in GB [Integer]
        :param slave_instance_volume_type: volume type [Integer]
        :param slave_instance_volume_count: volume count [Integer]
        :param key_name: key to connect via SSH [String]
        :param arn: aws iam role [String]
        :param level: logging level [String]
        """
        # logger
        self._logger = Logger(logger_name=__name__ + '.emr', level=level)

        # cluster
        self._created_at = None
        self._cluster_id = None
        self._cluster_name = name
        self._aws_region = aws_region
        self._applications = applications
        self._logs = logs
        self._bootstrap = bootstrap
        self._script = script
        self._emr_version = emr_version
        self._subnet_id = subnet_id
        self._security_group = security_group

        self._master_instance_type = master_instance_type
        self._master_instance_count = master_instance_count
        self._master_instance_volume_size = master_instance_volume_size
        self._master_instance_volume_type = master_instance_volume_type
        self._master_instance_volume_count = master_instance_volume_count

        self._slave_instance_type = slave_instance_type
        self._slave_instance_count = slave_instance_count
        self._slave_instance_volume_size = slave_instance_volume_size
        self._slave_instance_volume_type = slave_instance_volume_type
        self._slave_instance_volume_count = slave_instance_volume_count

        self._key_name = key_name
        self._arn = arn
        self._steps = []

        try:
            if self._arn:
                self.sts_client = boto3.client('sts')
                assumed_role = self.sts_client.assume_role(
                    RoleArn=self._arn,
                    RoleSessionName='emr-session'
                )

                credentials = assumed_role['Credentials']
                self.client = boto3.client(
                    'emr',
                    region_name=self._aws_region,
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                )
                self._logger.debug('ARN = {}'.format(self._arn))
            else:
                self._client = boto3.client('emr', region_name=self._aws_region)

        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def create_cluster(self):
        """
        Create EMR cluster with the steps given
        :return: cluster id [String]
        """
        if self._steps:
            apps = []
            for app in self._applications:
                apps.append({'Name': app})

            instance_groups = []
            master_instance = {
                "Name": "Master",
                "InstanceRole": "MASTER",
                "InstanceType": self._master_instance_type,
                "InstanceCount": self._master_instance_count,
                "EbsConfiguration": {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "SizeInGB": self._master_instance_volume_size,
                                "VolumeType": self._master_instance_volume_type
                            },
                            "VolumesPerInstance": self._master_instance_volume_count
                        }
                    ]
                }
            }

            instance_groups.append(master_instance)

            if self._slave_instance_type:
                slave_instance = {
                    "Name": "Core",
                    "InstanceRole": "CORE",
                    "InstanceType": self._slave_instance_type,
                    "InstanceCount": self._slave_instance_count,
                    "EbsConfiguration": {
                        "EbsBlockDeviceConfigs": [
                            {
                                "VolumeSpecification": {
                                    "SizeInGB": self._slave_instance_volume_size,
                                    "VolumeType": self._slave_instance_volume_type
                                },
                                "VolumesPerInstance": self._slave_instance_volume_count
                            }
                        ]
                    }
                }
                instance_groups.append(slave_instance)

            self._created_at = get_current_timestamp()

            response = self._client.run_job_flow(
                Name=self._cluster_name,
                LogUri=self._logs,
                ReleaseLabel=self._emr_version,
                Applications=apps,
                Instances={
                    'InstanceGroups': instance_groups,
                    'Ec2KeyName': self._key_name,
                    'KeepJobFlowAliveWhenNoSteps': False,
                    'TerminationProtected': False,
                    'Ec2SubnetId': self._subnet_id,
                    'EmrManagedMasterSecurityGroup': self._security_group,
                    'EmrManagedSlaveSecurityGroup': self._security_group
                },
                Configurations=[
                    {
                        "Classification": "spark",
                        "Properties": {
                            "maximizeResourceAllocation": "true"
                        }
                    },
                    {
                        "Classification": "mapred-site",
                        "Properties": {
                            "mapred.output.committer.class": "org.apache.hadoop.mapred.FileOutputCommitter",
                            "mapreduce.fileoutputcommitter.algorithm.version": "2"
                        }
                    }
                ],

                BootstrapActions=[
                    {
                        'Name': 'Configure Cluster',
                        'ScriptBootstrapAction': {
                            'Path': self._bootstrap
                        }
                    }
                ],
                Tags=[
                    {
                        'Key': 'application',
                        'Value': 'amazonas'
                    },
                    {
                        'Key': 'project',
                        'Value': 'panamera'
                    },
                    {
                        'Key': 'team',
                        'Value': 'bi'
                    },
                    {
                        'Key': 'product_name',
                        'Value': 'Panamera-BI'
                    }
                ],
                EbsRootVolumeSize=30,
                ScaleDownBehavior='TERMINATE_AT_TASK_COMPLETION',
                VisibleToAllUsers=True,
                JobFlowRole='EMR_EC2_DefaultRole',
                ServiceRole='EMR_DefaultRole',
                Steps=self._steps
            )
            self._cluster_id = response['JobFlowId']

        else:
            self._logger.warning('No steps to run')

        return self._cluster_id

    def add_hadoop_step(self, name, args):
        """
        Add Hadoop step to run
        :param name: step name [String]
        :param args: list of args to run the script [List<String>]
        :return:
        """
        step = {
            'Name': name,
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    'spark-submit',
                    '--deploy-mode', 'client',
                    '--master', 'yarn',
                    self._script
                ]
            }
        }
        step['HadoopJarStep']['Args'] = step['HadoopJarStep']['Args'] + args
        self._steps.append(step)

    def get_steps_by_status(self, status):
        """
        Get steps with a given status
        :param status: status name [String]
        :return: list of steps with the status given [Dict]
        """
        steps = []
        if self._cluster_id:
            try:
                response = self._client.list_steps(
                    ClusterId=self._cluster_id
                )

                if 'Steps' in response:
                    steps = response['Steps']

                    for step in steps:
                        if 'Status' in step:
                            if 'State' in step['Status']:
                                if step['Status']['State'] == status.upper():
                                    steps += step

            except Exception as _:
                pass

        return steps

    def get_step_status(self, step_id):
        """
        Get step status
        :param step_id: step identifier [String]
        :return: status of the step [Dict]
        """
        status = None
        if self._cluster_id:
            try:
                response = self._client.list_steps(
                    ClusterId=self._cluster_id
                )

                if 'Steps' in response:
                    steps = response['Steps']

                    for step in steps:
                        if step['Id'] == step_id:
                            status = step
                            break

            except Exception as _:
                pass

        return status

    def get_cluster_status(self):
        """
        Get cluster status
        :return: cluster status State, Code and Message [Dictionary<String>]
        """
        status = {
            'State': None,
            'Code': None,
            'Message': None
        }

        if self._cluster_id:
            try:
                response = self._client.list_clusters(
                    CreatedAfter=self._created_at,
                )
                if 'Clusters' in response:
                    for cluster in response['Clusters']:
                        if cluster['Id'] == self._cluster_id:

                            status['State'] = cluster['Status']['State']
                            if 'Code' in cluster['Status']['StateChangeReason']:
                                status['Code'] = cluster['Status']['StateChangeReason']['Code']

                            if 'Message' in cluster['Status']['StateChangeReason']:
                                status['Message'] = cluster['Status']['StateChangeReason']['Message']
            except Exception as _:
                pass

        return status

    def get_steps(self):
        """
        Get list of steps
        :return: lists of steps [List<Dict>]
        """
        return self._steps

    def count_steps(self):
        """
        Count number of steps
        :return:
        """
        return len(self._steps)

    def get_cluster_id(self):
        """
        Get cluster identifier
        :return: cluster identifier [String]
        """
        return self._cluster_id

    def get_step_id(self, step_name):
        """
        Get step identifier
        :param step_name: step name [String]
        :return: status of the step [Dict]
        """
        id = None
        if self._cluster_id:
            try:
                response = self._client.list_steps(
                    ClusterId=self._cluster_id
                )

                if 'Steps' in response:
                    steps = response['Steps']

                    for step in steps:
                        if step['Name'] == step_name:
                            id = step['Id']

            except Exception as _:
                pass

        return id

    def get_cluster_name(self):
        """
        Get the cluster name
        :return: cluster name [String]
        """
        return self._cluster_name
