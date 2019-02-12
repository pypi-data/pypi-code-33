#!/usr/bin/env python
# -*- coding: utf-8 -*-
from click.testing import CliRunner

import migration_runner.cli


class TestCLI(object):
    """Tests for CLI class in `migration_runner` package."""

    def test_cli_no_arguments(self):
        runner = CliRunner()
        result = runner.invoke(migration_runner.cli.main)
        assert 'Error: Missing argument' in result.output

    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(migration_runner.cli.main, ['--help'])
        assert result.exit_code == 0
        assert 'Show this message and exit.' in result.output

    def test_cli_version(self):
        runner = CliRunner()
        result = runner.invoke(migration_runner.cli.main, ['-v'])
        assert result.exit_code == 0
        assert ', version' in result.output

    def test_cli_single_file(self, mocker, controller, db_params_tup,
                             db_params_dict):
        mocker.patch('migration_runner.Controller.process_single_file')

        runner = CliRunner()
        runner.invoke(migration_runner.cli.main, [
            '--single-file',
            'test.sql',
            'testdir',
            db_params_dict['user'],
            db_params_dict['host'],
            db_params_dict['database'],
            db_params_dict['password']
        ])

        controller.process_single_file.assert_called_with(db_params_tup,
                                                          'test.sql')

    def test_cli_directory(self, mocker, controller, db_params_tup,
                           db_params_dict):
        mocker.patch(
            'migration_runner.Controller.process_migrations_in_directory')

        runner = CliRunner()
        runner.invoke(migration_runner.cli.main, [
            'testdir',
            db_params_dict['user'],
            db_params_dict['host'],
            db_params_dict['database'],
            db_params_dict['password']
        ])

        controller.process_migrations_in_directory.assert_called_with(
            db_params_tup,
            'testdir'
        )

    def test_cli_loglevel_debug(self, mocker, db_params_dict):
        mocker.patch(
            'migration_runner.Controller.process_migrations_in_directory')

        runner = CliRunner()
        result = runner.invoke(migration_runner.cli.main, [
            '-l',
            'DEBUG',
            'testdir',
            db_params_dict['user'],
            db_params_dict['host'],
            db_params_dict['database'],
            db_params_dict['password']
        ])

        assert "CLI execution start" in result.output
