import sys
import box
import click
from . import exceptions


config = box.Box(accept_imported=False,
                 scan_recursively=True,
                 result_file=sys.stderr,
                 black_list=[],
                 error_handler=exceptions.default_error_handler,
                 expected_error_cls=exceptions.ExpectedError,
                 usage_error_cls=click.UsageError,
                 prog_name=None,
                 version_option=None,
                 help_option_names=None,
                 )


def get_config():
    """This provides the same config that is used in the user module"""
    try:
        return sys.modules['kickoff'].config
    except KeyError:
        # kickoff module doesn't seem to be imported in the user module
        return config
