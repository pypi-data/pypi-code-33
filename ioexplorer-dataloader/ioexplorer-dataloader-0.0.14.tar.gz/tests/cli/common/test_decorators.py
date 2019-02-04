from unittest import mock

import ast

import click
from click.testing import CliRunner

from ioexplorer_dataloader import cli


@click.command()
@cli.common.decorators.add_env_variables
def _env_cli(_env):
    print(_env)


def test_env_variables_taken():
    "Test that an environment variables are correctly parsed."
    runner = CliRunner(
        env={
            "IOEXPLORER_DATABASE_NAME": "mydatabase",
            "IOEXPLORER_DATABASE_HOST": "localhost",
            "IOEXPLORER_DATABASE_PORT": "5432",
            "IOEXPLORER_DATABASE_USERNAME": "ryan",
            "IOEXPLORER_DATABASE_PASSWORD": "password",
        }
    )
    result = runner.invoke(_env_cli)
    assert result.exit_code == 0
    assert ast.literal_eval(result.output) == {
        "name": "mydatabase",
        "host": "localhost",
        "port": "5432",
        "username": "ryan",
        "password": "password",
    }


def test_error_when_env_variable_missing():
    "Test that an error is thrown when >=1 environment variable is missing."
    runner = CliRunner(
        env={
            # 'IOEXPLORER_DATABASE_NAME': 'mydatabase',
            "IOEXPLORER_DATABASE_HOST": "localhost",
            "IOEXPLORER_DATABASE_PORT": "5432",
            "IOEXPLORER_DATABASE_USERNAME": "ryan",
            "IOEXPLORER_DATABASE_PASSWORD": "password",
        }
    )
    result = runner.invoke(_env_cli)
    assert result.exit_code == 1
    assert (
        result.output
        == "ERROR: The `IOEXPLORER_DATABASE_NAME` environment variable was not set. Exiting.\n"
    )

    runner = CliRunner(
        env={
            "IOEXPLORER_DATABASE_NAME": "mydatabase",
            "IOEXPLORER_DATABASE_HOST": "localhost",
            "IOEXPLORER_DATABASE_PORT": "5432",
            "IOEXPLORER_DATABASE_USERNAME": "ryan",
            # 'IOEXPLORER_DATABASE_PASSWORD': 'password'
        }
    )
    result = runner.invoke(_env_cli)
    assert result.exit_code == 1
    assert (
        result.output
        == "ERROR: The `IOEXPLORER_DATABASE_PASSWORD` environment variable was not set. Exiting.\n"
    )

    runner = CliRunner(env={})
    result = runner.invoke(_env_cli)
    assert result.exit_code == 1
    # IOEXPLORER_DATABASE_NAME is the first variable checked.
    assert (
        result.output
        == "ERROR: The `IOEXPLORER_DATABASE_NAME` environment variable was not set. Exiting.\n"
    )


class _MockEngine:
    "A fake engine class with a connect attribute."
    connect = None


def _create_engine(conn_string, paramstyle):
    "A fake sqlalchemy.create_engine function that doesn't try to connect to a database."
    engine = _MockEngine()
    engine.connect = lambda: conn_string
    return engine


def test_connect_to_db():
    "Test the connect_to_db decorator works as expected."
    with mock.patch(
        "ioexplorer_dataloader.cli.common.decorators.create_engine", _create_engine
    ):

        def _wrapped(conn, engine, _env):
            return conn, engine, _env

        conn, engine, _env = cli.common.decorators.connect_to_db(_wrapped)(
            _env={
                "name": "mydatabase",
                "host": "localhost",
                "port": "5432",
                "username": "ryan",
                "password": "password",
            }
        )
        assert conn == "postgres://ryan:password@localhost:5432/mydatabase"
        assert isinstance(engine, _MockEngine)
        assert isinstance(_env, dict)
