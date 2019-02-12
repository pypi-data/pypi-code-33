#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mysql.connector
from mock import call


class TestController(object):
    """Tests for Controller class in `migration_runner` package."""

    def test_process_single_file_calls_apply(
        self, controller, database_tools, mocker, db_params_tup,
        sql_filename_expected
    ):
        mocker.patch(
            'migration_runner.DatabaseTools.apply_migration')
        controller.process_single_file(db_params_tup, sql_filename_expected)

        database_tools.apply_migration.assert_called_with(
            db_params_tup,
            sql_filename_expected
        )

    def test_update_current_version_calls_connect(
        self, controller, mocker, db_params_tup, db_params_dict
    ):
        mocker.patch('mysql.connector.connect')

        controller.update_current_version(db_params_tup, 45)

        mysql.connector.connect.assert_called_with(**db_params_dict)

    def test_update_current_version_executes_update(
        self, controller, mocker, db_params_tup
    ):
        mocker.patch('mysql.connector.connect')

        mock_connection = mysql.connector.connect.return_value
        mock_cursor = mock_connection.cursor.return_value

        controller.update_current_version(db_params_tup, 45)

        mock_cursor.execute.assert_has_calls([
            call("UPDATE versionTable SET version = \'45\'"),
            call("SELECT version FROM versionTable LIMIT 1"),
        ])

    def test_update_current_version_returns_new_version(
        self, controller, mocker, db_params_tup
    ):
        mocker.patch('mysql.connector.connect')

        expected = 45

        mock_connection = mysql.connector.connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = (expected,)

        result = controller.update_current_version(db_params_tup, expected)

        assert result == expected

    def test_update_current_version_returns_0_if_version_invalid(
        self, controller, mocker, db_params_tup
    ):
        mocker.patch('mysql.connector.connect')

        mock_connection = mysql.connector.connect.return_value
        mock_cursor = mock_connection.cursor.return_value

        mock_cursor.execute.side_effect = \
            mysql.connector.errors.DataError(
                "1366 (22007): Incorrect integer value: 'five' for column"
                " `versionTable`.`version` at row 1")

        result = controller.update_current_version(db_params_tup, 'five')

        assert result == 0

    def test_process_migrations_calls_apply(
        self, controller, database_tools, mocker, db_params_tup,
        sorted_migrations_tuple_list
    ):
        mocker.patch('migration_runner.DatabaseTools.apply_migration')
        mocker.patch('migration_runner.Controller.update_current_version')

        controller.process_migrations(db_params_tup, 0,
                                      sorted_migrations_tuple_list)

        database_tools.apply_migration.assert_has_calls([
            call(db_params_tup, '/tmp/001.createtable.sql'),
            call(db_params_tup, '/tmp/2-createtable.sql'),
            call(db_params_tup, '/tmp/045.createtable.sql'),
            call(db_params_tup, '/tmp/60.createtable.sql'),
        ])

    def test_process_migrations_calls_update(
        self, controller, mocker, db_params_tup, sorted_migrations_tuple_list
    ):
        mocker.patch('migration_runner.DatabaseTools.apply_migration')
        mocker.patch('migration_runner.Controller.update_current_version')

        controller.process_migrations(db_params_tup, 0,
                                      sorted_migrations_tuple_list)

        controller.update_current_version.assert_has_calls([
            call(db_params_tup, 1),
            call(db_params_tup, 2),
            call(db_params_tup, 45),
            call(db_params_tup, 60)
        ], any_order=True)

    def test_process_migrations_returns_expected(
        self, controller, mocker, db_params_tup, sorted_migrations_tuple_list
    ):
        mocker.patch('migration_runner.DatabaseTools.apply_migration')
        mocker.patch('migration_runner.Controller.update_current_version')

        controller.update_current_version.return_value = 60

        db_version, total_processed = controller.process_migrations(
            db_params_tup, 0, sorted_migrations_tuple_list)

        assert db_version == 60
        assert total_processed == 4

    def test_process_migrations_in_directory_calls_methods(
        self, controller, database_tools, helpers, mocker, db_params_tup
    ):
        mocker.patch('migration_runner.Helpers.populate_migrations')
        mocker.patch('migration_runner.Helpers.get_unprocessed_migrations')
        mocker.patch('migration_runner.DatabaseTools.fetch_current_version')
        mocker.patch('migration_runner.Controller.process_migrations')

        helpers.populate_migrations.return_value = []
        helpers.get_unprocessed_migrations.return_value = []
        database_tools.fetch_current_version.return_value = 0
        controller.process_migrations.return_value = (0, 0)

        controller.process_migrations_in_directory(db_params_tup, "")

        helpers.populate_migrations.assert_called_with("")
        database_tools.fetch_current_version.assert_called_with(db_params_tup)
        helpers.get_unprocessed_migrations.assert_called_with(0, [])
        controller.process_migrations.assert_called_with(db_params_tup, 0, [])

    def test_process_migrations_in_directory_logs_expected(
        self, controller, database_tools, logger, helpers, mocker,
        db_params_tup
    ):
        mocker.patch('logging.Logger.info')
        mocker.patch('logging.Logger.debug')
        mocker.patch('migration_runner.Helpers.populate_migrations')
        mocker.patch('migration_runner.Helpers.get_unprocessed_migrations')
        mocker.patch('migration_runner.DatabaseTools.fetch_current_version')
        mocker.patch('migration_runner.Controller.process_migrations')

        helpers.populate_migrations.return_value = []
        helpers.get_unprocessed_migrations.return_value = []
        database_tools.fetch_current_version.return_value = 0
        controller.process_migrations.return_value = (0, 0)

        controller.process_migrations_in_directory(db_params_tup, "")

        logger.debug.assert_called_with("Migrations found: 0")

        logger.info.assert_has_calls([
            call("Migrations yet to be processed: 0 (out of 0 in dir)"),
            call("Database version now 0 after processing 0 migrations. "
                 "Remaining: 0.")
        ], any_order=True)
