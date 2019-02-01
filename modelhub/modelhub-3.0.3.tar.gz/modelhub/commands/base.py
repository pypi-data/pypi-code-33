# -*- coding: utf-8 -*-
import click
from click import argument, option, types  # noqa
import contextlib
import logging
import logging.config
from modelhub.core import conf


@click.group()
def main():
    "Modelhub - a Model management system"
    pass


def register(name):
    def wrapper(command_cls):
        assert issubclass(command_cls, BaseCommand)
        command_cls.name = name

        @contextlib.wraps(command_cls.run)
        def command(*args, **kwargs):
            debug = kwargs.pop("debug")
            verbose = kwargs.pop("verbose")
            command = command_cls(verbose)
            if debug:
                import ipdb  # noqa
                with ipdb.launch_ipdb_on_exception():
                    command.run(*args, **kwargs)
            else:
                command.run(*args, **kwargs)
        for arg in reversed(command_cls.add_arguments()):
            command = arg(command)
        main.add_command(click.command(command_cls.name)(command))
        return command_cls
    return wrapper


class BaseCommand:

    def __init__(self, verbose=False):
        self.verbose = verbose
        logging.config.dictConfig(conf.LOG_CONFIG)
        self.logger = logging.getLogger(self.name)
        if self.verbose:
            self.logger.setLevel(logging.DEBUG)

    @staticmethod
    def echo(*args, **kwargs):
        return click.echo(*args, **kwargs)

    arguments = []

    @classmethod
    def add_arguments(cls):
        return cls.arguments + [
            option("--debug", is_flag=True, help="Debug Mode"),
            option("-v", "--verbose", is_flag=True, help="verbose Mode")
        ]

    def get_user_info(self):
        if conf.USER_NAME is None or conf.USER_EMAIL is None:
            self.echo("""You have to set user infomation on ~/.modelhubrc
Example:
[user]
name = Jack Jones
email = jack@example.com
                """)
            raise ValueError
        return conf.USER_NAME, conf.USER_EMAIL

    def log_info(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.info()
        """
        self.logger.info(msg, *args, **kwargs)

    def log_error(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.error()
        """
        self.logger.error(msg, *args, **kwargs)

    def log_debug(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.debug()
        """
        self.logger.debug(msg, *args, **kwargs)

    def log_warning(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.warning()
        """
        self.logger.warning(msg, *args, **kwargs)

    def log_exception(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.exception()
        """
        self.logger.exception(msg, *args, **kwargs)

    def log_critical(self, msg, *args, **kwargs):
        """
        log a message, more details to see logging.critical()
        """
        self.logger.critical(msg, *args, **kwargs)
