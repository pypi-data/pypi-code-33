import click

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
    version = pkg_resources.require("octohot")[0].version
    click.echo(f'version: {version}')


cli.add_command(version)

from octohot.cli.sync import sync
cli.add_command(sync)

# from octohot.cli.regex.find import find
# cli.add_command(find)

# from octohot.cli.regex.replace import replace
# cli.add_command(replace)

from octohot.cli.apply import apply
cli.add_command(apply)

from .git import git
cli.add_command(git.git)

from .github import github
cli.add_command(github.github)

from .regex import regex
cli.add_command(regex.regex)

if __name__ == '__main__':
    cli()
