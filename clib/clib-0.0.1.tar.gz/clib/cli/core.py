import click

from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from clib.cli.aliased_group import AliasedGroup


@with_plugins(iter_entry_points('clib.plugins'))
@click.group(
    cls=AliasedGroup,
)
@click.version_option()
@click.pass_context
def main(ctx):
    """ A simple and modular CLI that helps automate common tasks.
    """
    pass
