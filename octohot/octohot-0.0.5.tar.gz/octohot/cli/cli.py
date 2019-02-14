import click
from octohot.cli.sync import sync
from octohot.cli.apply import apply
from .git import git
from .github import github
from .regex import regex


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enables verbose mode.')
def cli(verbose=True):
    """Command line interface for the octohot package"""
    if verbose:
        import logging
        logging.getLogger().setLevel(logging.INFO)


@click.command()
def version():
    """Display the current version."""
    import pkg_resources  # part of setuptools
    version_str = pkg_resources.require("octohot")[0].version
    click.echo('version: %s' % version_str)


cli.add_command(version)
cli.add_command(sync)
cli.add_command(apply)
cli.add_command(git.git)
cli.add_command(github.github)
cli.add_command(regex.regex)

if __name__ == '__main__':
    cli()
