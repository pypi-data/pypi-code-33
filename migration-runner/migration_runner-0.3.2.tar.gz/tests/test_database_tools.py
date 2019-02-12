#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io

import mysql.connector
import pytest


class TestDatabaseTools(object):
    """Tests for DatabaseTools class in `migration_runner` package."""

    def test_connect_database_invalid_params(
        self, database_tools, db_params_tup
    ):
        with pytest.raises(SystemExit):
            database_tools.connect_database(db_params_tup)

    def test_connect_database_mysql_library_called(
        self, database_tools, mocker, db_params_tup, db_params_dict
    ):
        mocker.patch('mysql.connector.connect')
        database_tools.connect_database(db_params_tup)

        mysql.connector.connect.assert_called_with(**db_params_dict)

    def test_fetch_current_version_calls_connect(
        self, database_tools, mocker, db_params_tup, db_params_dict
    ):
        mocker.patch('mysql.connector.connect')
        database_tools.fetch_current_version(db_params_tup)

        mysql.connector.connect.assert_called_with(**db_params_dict)

    def test_fetch_current_version_fetches_expected_value(
        self, database_tools, mocker, db_params_tup
    ):
        expected = 45
        mocker.patch('mysql.connector.connect')

        mock_connection = mysql.connector.connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = (expected,)

        result = database_tools.fetch_current_version(db_params_tup)

        assert result == expected

    def test_fetch_current_version_invalid_db_params(
        self, database_tools, db_params_tup
    ):
        with pytest.raises(SystemExit):
            database_tools.fetch_current_version(db_params_tup)

    def test_fetch_current_version_no_version_in_database(
        self, database_tools, mocker, db_params_tup
    ):
        mocker.patch('mysql.connector.connect')

        mock_connection = mysql.connector.connect.return_value
        mock_cursor = mock_connection.cursor.return_value

        mock_cursor.fetchone.side_effect = \
            mysql.connector.errors.ProgrammingError(
                "1146 (42S02): Table 'versionTable' doesn't exist")

        result = database_tools.fetch_current_version(db_params_tup)

        assert result == 0

    def test_apply_migration_expected_opens_file(
        self, database_tools, tmpdir, mocker, db_params_tup,
        sql_filename_expected
    ):
        mocker.patch('mysql.connector.connect')
        mocker.patch('io.open')

        filepath = tmpdir.join(sql_filename_expected)
        filepath.write("test")

        database_tools.apply_migration(db_params_tup, str(filepath))

        io.open.assert_called_with(str(filepath))

    def test_apply_migration_expected_calls_connect(
        self, database_tools, tmpdir, mocker, db_params_tup, db_params_dict,
        sql_filename_expected
    ):
        mocker.patch('mysql.connector.connect')

        filepath = tmpdir.join(sql_filename_expected)
        filepath.write("test")

        database_tools.apply_migration(db_params_tup, str(filepath))

        mysql.connector.connect.assert_called_with(**db_params_dict)

    def test_apply_migration_expected_executes_file(
        self, database_tools, tmpdir, mocker, db_params_tup,
        sql_filename_expected
    ):
        mocker.patch('mysql.connector.connect')

        filepath = tmpdir.join(sql_filename_expected)
        filepath.write("test")

        mock_connection = mysql.connector.connect.return_value
        mock_cursor = mock_connection.cursor.return_value

        database_tools.apply_migration(db_params_tup, str(filepath))

        mock_cursor.execute.assert_called_with("test", multi=True)
