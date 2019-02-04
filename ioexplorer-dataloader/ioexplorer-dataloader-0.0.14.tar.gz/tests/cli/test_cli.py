import os
import textwrap
from ioexplorer_dataloader import cli
from click.testing import CliRunner


def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert result.output == textwrap.dedent(
        """\
        Usage: cli [OPTIONS] COMMAND [ARGS]...
        
        Options:
          --help  Show this message and exit.
        
        Commands:
          database
          dataset
    """
    )
