import click
import sys
import logging
from contextlib import contextmanager
from .logger import log
from .helpers import in_dev_mode, abort


class ExpectedError(Exception):
    """Base class for these errors which should be shown without traceback
    """
    exit_code = 3


def default_error_handler(exc):
    """Default handler for ExpectedError or any custom expected_error_cls
    """
    print(f"Error: {exc}", file=sys.stderr)


@contextmanager
def exception_guard(error_handler, usage_error_cls, expected_error_cls):
    """Suppress traceback or translate Exception into click.UsageError so that click can show context help
    """
    try:
        yield
    except usage_error_cls as exc:
        log.debug(f"UsageError occurred: {exc!r}")
        raise click.UsageError(str(exc)) from exc
    except expected_error_cls as exc:
        log.debug(f"ExpectedError occurred: {exc!r}")
        error_handler(exc)
        if hasattr(exc, 'exit_code'):
            abort(exc.exit_code)
        else:
            abort(ExpectedError.exit_code)


@contextmanager
def internal_exception_guard():
    """Suppress traceback unless we are in DEV mode
    """
    try:
        yield
    except Exception as exc:
        if in_dev_mode():
            raise
        else:
            default_error_handler(exc)
            abort()
