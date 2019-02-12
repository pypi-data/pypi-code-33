# -*- coding: utf-8 -*-

"""Console script for migration_runner."""
import logging
import sys
import types

import click
import click_log
from click_log import ClickHandler

# Monkey-patch click_log ColorFormatter class format method to add timestamps
from migration_runner.controller import Controller


def custom_format(self, record):
    if not record.exc_info:
        level = record.levelname.lower()
        msg = record.getMessage()

        prefix = self.formatTime(record, self.datefmt) + " - "
        level_prefix = '{}: '.format(level)
        if level in self.colors:
            level_prefix = click.style(level_prefix, **self.colors[level])
        prefix += level_prefix

        msg = '\n'.join(prefix + x for x in msg.splitlines())
        return msg
    return logging.Formatter.format(self, record)


logger = logging.getLogger(__name__)
click_log.basic_config(logger)

_default_handler = ClickHandler()
_default_handler.formatter = click_log.ColorFormatter()
_default_handler.formatter.format = types.MethodType(
    custom_format,
    _default_handler.formatter
)

logger.handlers = [_default_handler]


@click.command()
@click.argument('sql_directory')
@click.argument('db_user')
@click.argument('db_host')
@click.argument('db_name')
@click.argument('db_password')
@click.option('-s', '--single-file', required=False, type=str,
              help='Filename of single SQL script to process.')
@click_log.simple_verbosity_option(logger, '--loglevel', '-l')
@click.version_option(None, '-v', '--version')
def main(sql_directory, db_user, db_host, db_name, db_password, single_file):
    """A CLI tool for executing SQL migrations in sequence."""

    logger.debug("CLI execution start")
    db_params = (db_host, db_user, db_password, db_name)

    controller = Controller(logger)

    if single_file is not None:
        controller.process_single_file(db_params, single_file)
    else:
        controller.process_migrations_in_directory(db_params, sql_directory)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
