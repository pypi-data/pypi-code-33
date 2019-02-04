import os
import click
from functools import wraps


def database_name_argument(func):
    return click.argument(
        "name", default=lambda: os.environ.get("IOEXPLORER_DATABASE_NAME", None)
    )(func)
