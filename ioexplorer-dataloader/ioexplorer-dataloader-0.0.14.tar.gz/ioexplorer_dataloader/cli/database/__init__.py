import os
import click

from .helpers import start_database, kill_database, shell_database, migrate_database
from ..common.arguments import database_name_argument
from ..common.decorators import add_env_variables
from ..common.logging import error


@click.group()
def database():
    pass  # pragma: no cover


@database.command(help="Start the database with name NAME.")
@add_env_variables
def start(_env):
    start_database(
        database_name=_env["name"],
        database_port=_env["port"],
        database_username=_env["username"],
        database_password=_env["password"],
    )


@database.command(help="Kill the database.")
@add_env_variables
@click.confirmation_option(
    prompt=click.style("Are you sure you want to delete the database?", fg="red"),
    help="Confirm the deletion (will not confirm before deletion if set!)",
)
def kill(_env):
    kill_database(database_name=_env["name"])


@database.command(help="Migrate the NAME database")
@add_env_variables
def migrate(_env):
    migrate_database(
        database_name=_env["name"],
        database_host=_env["host"],
        database_port=_env["port"],
        database_username=_env["username"],
        database_password=_env["password"],
    )


@database.command(help="Open a psql shell for the NAME database")
@add_env_variables
def shell(_env):
    shell_database(_env["name"], _env["username"], _env["password"])
