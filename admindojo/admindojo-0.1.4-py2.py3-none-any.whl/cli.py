# -*- coding: utf-8 -*-

"""Console script for admindojo."""
import sys
import click
from click_default_group import DefaultGroup

import admindojo.admindojo as admindojo


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(cls=DefaultGroup, default='check', default_if_no_args=True)
def cli():
    """
    admindojo client\n
    run withouth options to check your training result
    """
    pass

@click.command()
def check():
    """
    Check your result
    """
    admindojo.check()

@click.command()
def update():
    """
    Show update instructions
    """
    admindojo.update()

@click.command()
def show():
    """
    Show result
    """
    admindojo.main()

cli.add_command(check)
cli.add_command(show)
cli.add_command(update)

if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
