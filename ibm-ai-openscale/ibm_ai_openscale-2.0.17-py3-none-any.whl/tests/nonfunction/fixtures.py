# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from configparser import ConfigParser
import pytest
import json
import os
import psycopg2
import jaydebeapi
from psycopg2.sql import Identifier, SQL
from datetime import datetime, timedelta
from pytz import timezone
from ibm_ai_openscale import APIClient, APIClient4ICP

yesterday = datetime.now(timezone('UTC')) - timedelta(days=1)


if "TEST_DIR" in os.environ:
    configDir = os.environ['TEST_DIR'] + "config.ini"
else:
    configDir = "./config.ini"

config = ConfigParser()
config.read(configDir)


@pytest.fixture
def environment():
    if "ENV" in os.environ:
        return os.environ['ENV']
    else:
        return "YP_QA"


@pytest.fixture
def schema_name(environment):
    return config.get(environment, 'schema_name')


@pytest.fixture
def schema_name2(environment):
    return config.get(environment, 'schema_name2')


@pytest.fixture
def aios_credentials(environment):
    return json.loads(config.get(environment, 'aios_credentials'))


@pytest.fixture
def database_credentials(environment):
    if config.has_option(environment, 'database_credentials'):
        return json.loads(config.get(environment, 'database_credentials'))
    elif config.has_option(environment, 'postgres_credentials'):
        return json.loads(config.get(environment, 'postgres_credentials'))
    elif config.has_option(environment, 'db2_datamart'):
        return json.loads(config.get(environment, 'db2_datamart'))
    else:
        raise Exception("There is no database in config!")


@pytest.fixture
def db2_schema_name():
    return json.loads(config.get(environment, 'db2_schema'))


@pytest.fixture
def wml_credentials():
    return json.loads(config.get(environment, 'wml_credentials'))


@pytest.fixture
def ai_client(environment, aios_credentials):
    if "ICP" in environment:
        return APIClient4ICP(aios_credentials)
    else:
        return APIClient(aios_credentials)


@pytest.fixture
def prepare_env(ai_client, environment, database_credentials, schema_name, internal=False):

    for uid in ai_client.data_mart.subscriptions.get_uids():
        print('Deleting \'{}\' subscription.'.format(uid))
        try:
            ai_client.data_mart.subscriptions.delete(uid)
        except Exception as e:
            print('Deleting of subscription failed:', e)

    for uid in ai_client.data_mart.bindings.get_uids():
        try:
            ai_client.data_mart.bindings.delete(uid)
        except:
            pass
    try:
        ai_client.data_mart.delete()
    except:
        pass

    if internal:
        return

    db_credentials = database_credentials
    schema_name = schema_name

    if "ICP" in environment:
        clean_db2_icp_schema(db_credentials, schema_name)
    else:
        if 'postgres' in db_credentials['uri']:
            delete_schema(db_credentials, schema_name)
            create_schema(db_credentials, schema_name)
        elif 'db2' in db_credentials['uri']:
            clean_db2_schema(db_credentials, schema_name)
        else:
            raise Exception("Database {} not supported!".format(db_credentials))


def prepare_connection_postgres(postgres_credentials):
    uri = postgres_credentials['uri']

    import re
    res = re.search('^[0-9a-zA-Z]+://([0-9a-zA-Z]+):([0-9a-zA-Z]+)@([^:]+):([0-9]+)/([0-9a-zA-Z]+)$', uri)

    if res is None:
        raise Exception('Unexpected format of db uri: {}'.format(uri))

    username = res.group(1)
    password = res.group(2)
    host = res.group(3)
    port = res.group(4)
    database = res.group(5)

    return psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=host,
        port=port
    )


def prepare_connection_db2(db2_credentials):
    db2jcc_path = os.path.join(os.getcwd(), 'tools', 'db2jcc4.jar')
    return jaydebeapi.connect(
        'com.ibm.db2.jcc.DB2Driver',
        db2_credentials['jdbcurl'],
        [db2_credentials['username'], db2_credentials['password']],
        db2jcc_path
    )


def create_schema(postgres_credentials, schema_name):
    try:
        execute_sql_query(SQL("CREATE SCHEMA {}").format(Identifier(schema_name)), postgres_credentials)
    except psycopg2.Error as ex:
        print("Unable to create schema {}. Reason:\n{}".format(schema_name, ex.pgerror))


def delete_schema(postgres_credentials, schema_name):
    try:
        execute_sql_query(SQL("DROP SCHEMA {} CASCADE").format(Identifier(schema_name)), postgres_credentials)
        print("Schema {} dropped.".format(schema_name))
    except psycopg2.Error:
        print("Schema {} does not exist.".format(schema_name))


def delete_db2_schema(db2_credentials, schema_name):
    execute_sql_query("DROP SCHEMA {} CASCADE".format(schema_name), db2_credentials=db2_credentials)


def clean_db2_icp_schema(db2_credentials, schema_name):
    print(schema_name)

    print("QUERY: {}".format(""" select 'DROP TABLE "'||rtrim(tabschema)||'"."'||rtrim(tabname)||'"' from syscat.tables where OWNER = 'DB2INST1' and TABSCHEMA = '{}' and type = 'T' """.format(schema_name)))
    print("Cleaning db2 on ICP schema.")
    result = execute_sql_query(""" select 'DROP TABLE "'||rtrim(tabschema)||'"."'||rtrim(tabname)||'"' from syscat.tables where OWNER = 'DB2INST1' and TABSCHEMA = '{}' and type = 'T' """.format(schema_name), db2_credentials=db2_credentials)
    for query in result:
        print("Executing query: {}".format(query[0]))
        execute_sql_query(query[0], db2_credentials=db2_credentials)


def clean_db2_schema(db2_credentials, schema_name):
    for query in list(map(lambda table: """ DROP TABLE "{}"; """.format(table), list_db2_tables(db2_credentials=db2_credentials, schema_name=schema_name))):
        execute_sql_query(query, db2_credentials=db2_credentials)


def list_db2_tables(db2_credentials, schema_name):
    query_result = execute_sql_query(""" SELECT tabname FROM syscat.tables WHERE owner='{}' AND type='T' """.format(schema_name), db2_credentials=db2_credentials)
    db2_tables = []
    for record in query_result:
        db2_tables.append(record[0])

    return db2_tables


def print_schema_tables_info(postgres_credentials, schema_name):
    rows = execute_sql_query("SELECT * FROM information_schema.tables WHERE table_schema = '{}'".format(schema_name), postgres_credentials)

    for row in rows:
        print(row)


def wait_until_deleted(ai_client, binding_uid=None, subscription_uid=None, data_mart=None):
    uids_sum = sum([1 if b else 0 for b in [binding_uid, subscription_uid, data_mart]])

    if uids_sum > 1:
        raise Exception('More than one uid passed.')
    elif uids_sum == 0:
        raise Exception('No uids passed.')

    def can_be_found():
        if binding_uid is not None:
            try:
                print(ai_client.data_mart.bindings.get_details(binding_uid))
                return True
            except:
                return False
        elif subscription_uid is not None:
            try:
                print(ai_client.data_mart.subscriptions.get_details(subscription_uid))
                return True
            except:
                return False
        elif data_mart is not None:
            try:
                print(ai_client.data_mart.get_details())
                return True
            except Exception as e:
                print(e)
                return False

    import time

    print('Waiting for {} to delete...'.format(
        'binding with uid=\'{}\''.format(binding_uid) if binding_uid is not None
        else 'subscription with uid=\'{}\''.format(subscription_uid) if subscription_uid is not None
        else 'data_mart'
    ), end='')

    iterator = 0

    while can_be_found() and iterator < 20:
        time.sleep(3)
        print('.', end='')
        iterator += 1

    print(' DELETED')


def execute_sql_query(query, postgres_credentials=None, db2_credentials=None):
    if postgres_credentials is not None:
        conn = prepare_connection_postgres(postgres_credentials=postgres_credentials)
    elif db2_credentials is not None:
        conn = prepare_connection_db2(db2_credentials=db2_credentials)
    else:
        raise Exception("Credentials are not supported.")

    cursor = conn.cursor()
    cursor.execute(query)

    try:
        query_result = cursor.fetchall()
    except psycopg2.ProgrammingError as ex:
        query_result = ""
    except jaydebeapi.Error as ex:
        query_result = ""

    conn.commit()
    cursor.close()
    conn.close()

    return query_result
