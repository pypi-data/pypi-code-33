#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the database connection logic."""
from os import environ
import mock
import peewee
from pacifica.uniqueid.orm import OrmSync, UniqueIndex, UniqueIndexSystem


@mock.patch.object(UniqueIndex, 'database_connect')
def test_bad_db_connection(mock_db_connect):
    """Test a failed db connection."""
    mock_db_connect.side_effect = peewee.OperationalError(
        mock.Mock(), 'Error')
    environ['DATABASE_CONNECT_ATTEMPTS'] = '2'
    environ['DATABASE_CONNECT_WAIT'] = '2'
    hit_exception = False
    try:
        OrmSync.dbconn_blocking()
    except peewee.OperationalError:
        hit_exception = True
    del environ['DATABASE_CONNECT_ATTEMPTS']
    del environ['DATABASE_CONNECT_WAIT']
    assert hit_exception


def test_no_table_goc_version():
    """Test the get or create version with no table."""
    OrmSync.dbconn_blocking()
    OrmSync.update_tables()
    UniqueIndexSystem.drop_table()
    major, minor = UniqueIndexSystem.get_or_create_version()
    assert major == 0
    assert minor == 0


def test_update_tables_twice():
    """Test updating tables twice to verify completeness."""
    OrmSync.dbconn_blocking()
    OrmSync.update_tables()
    OrmSync.update_tables()
