import click
from click.testing import CliRunner

from ioexplorer_dataloader import cli


@click.command()
@cli.common.arguments.database_name_argument
def _cli(name):
    print(name)


def test_database_name_argument_env_variable_is_taken():
    "Test that an environment variable argument is taken."
    runner = CliRunner(env={"IOEXPLORER_DATABASE_NAME": "mydatabase"})
    result = runner.invoke(_cli)
    assert result.exit_code == 0
    assert result.output == "mydatabase\n"


def test_database_name_argument_command_line_data_is_taken():
    "Test that argument defined on the command line is taken."
    runner = CliRunner()
    result = runner.invoke(_cli, ["myotherdatabasename"])
    assert result.exit_code == 0
    assert result.output == "myotherdatabasename\n"


def test_database_name_argument_command_line_overrides_env():
    "Test that a command line argument overrides environment variable."
    runner = CliRunner(env={"IOEXPLORER_DATABASE_NAME": "mydatabase"})
    result = runner.invoke(_cli, ["myotherdatabasename"])
    assert result.exit_code == 0
    assert result.output == "myotherdatabasename\n"


def test_database_name_argument_default_is_none():
    "Test default argument is None."
    runner = CliRunner()
    result = runner.invoke(_cli)
    assert result.exit_code == 0
    assert result.output == "None\n"
