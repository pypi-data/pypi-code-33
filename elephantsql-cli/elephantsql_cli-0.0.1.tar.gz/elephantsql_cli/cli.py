#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: elephantsql_cli.cli
.. moduleauthor:: Malik S <amywoodehy@gmail.com>

This is the entry point for the command-line interface (CLI) application.  It
can be used as a handy facility for running the task from a command line.

.. note::

    To learn more about Click visit the
    `project website <http://click.pocoo.org/5/>`_.  There is also a very
    helpful `tutorial video <https://www.youtube.com/watch?v=kNke39OZ2k0>`_.

    To learn more about running Luigi, visit the Luigi project's
    `Read-The-Docs <http://luigi.readthedocs.io/en/stable/>`_ page.
"""
import errno
import logging
import os

import click
import requests

from .__init__ import __version__

LOGGING_LEVELS = {
    0: logging.NOTSET,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG
}  #: a mapping of `verbose` option counts to logging levels


def mkdir_p(path):
    """
    Emulates usage of `mkdir -p /folder/to/create`
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Context(object):
    """
    This is an information object that can be used to pass data between CLI functions.
    """

    def __init__(self):  # Note that this object must have an empty constructor.
        self.verbose: int = 0
        self._api_token = None
        self.api_url = 'https://api.elephantsql.com/api'
        self.conf_dir = os.path.expanduser('~/.local/share/elephantsql-cli/')
        self.conf_file = os.path.join(self.conf_dir, 'elephantsql.txt')
        mkdir_p(self.conf_dir)

    @property
    def api_token(self):
        """Read API token from file"""
        if self._api_token is None:
            with open(self.conf_file, 'r') as conf:
                self._api_token = conf.readline()
            if not self._api_token:
                raise ValueError('You need to set api token')
        return self._api_token

    @api_token.setter
    def api_token(self, api_token):
        """Set and save API token"""
        self._api_token = api_token
        click.echo(f'api token = {api_token}')
        with open(self.conf_file, 'w') as conf:
            conf.write(api_token)

    @property
    def session(self):
        """Generate pre-authenticated requests session"""
        session = requests.Session()
        session.auth = (None, self.api_token)
        return session


# pass_info is a decorator for functions that pass 'Info' objects.
#: pylint: disable=invalid-name
pass_ctx = click.make_pass_decorator(
    Context,
    ensure=True
)


# Change the options to below to suit the actual options for your task (or
# tasks).
@click.group()
@click.option('--verbose', '-v', count=True, help="Enable verbose output.")
@pass_ctx
def cli(ctx: Context, verbose: int):
    """
    ElephantSQL CLI entrypoint
    """
    # Use the verbosity count to determine the logging level...
    if verbose > 0:
        logging.basicConfig(
            level=LOGGING_LEVELS[verbose]
            if verbose in LOGGING_LEVELS
            else logging.DEBUG
        )
        click.echo(
            click.style(
                f'Verbose logging is enabled. '
                f'(LEVEL={logging.getLogger().getEffectiveLevel()})',
                fg='yellow'
            )
        )
    ctx.verbose = verbose


@cli.command()
@click.option('--api-token', prompt=True)
@pass_ctx
def register(ctx, api_token):
    """
    Saves API TOKEN from ElephantSQL.

    Usage
        $ elephant register
    :param api_token: token retrieved from elephantsql.com
    :return:
    """
    ctx.api_token = api_token


@cli.command()
def version():
    """
    Get the library version.
    """
    click.echo(click.style(f'{__version__}', bold=True))


@cli.command()
@click.option('--db', type=click.STRING)
@pass_ctx
def list_backups(ctx, db):
    """
    Lists available backups
    """
    query = {}
    if db:
        query['db'] = db
    response = ctx.session.get(f'{ctx.api_url}/backup', params=query)

    click.echo(response.status_code)
    click.echo(response.json())


@cli.command()
@click.option('--db', type=click.STRING)
@pass_ctx
def backup(ctx, db):
    """
    Creates backup for specified database, or for all
    """
    query = {}
    if db:
        query['db'] = db
    response = ctx.session.post(f'{ctx.api_url}/backup', data=query)
    click.echo(response.status_code)


@cli.command()
@click.argument('backup_id', type=click.INT)
@pass_ctx
def restore(ctx, backup_id):
    """
    Restores database by backup_id
    """
    response = ctx.session.post(f'{ctx.api_url}/backup', data={
        'backup_id': backup_id,
    })
    click.echo(response.status_code)


@cli.command()
@pass_ctx
def alarms(ctx):
    """
    Get list of active alarms
    """
    response = ctx.session.get(f'{ctx.api_url}/alarms')

    click.echo(response.status_code)
    click.echo(response.json())
