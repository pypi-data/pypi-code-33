import logging
import sys
from traceback import TracebackException

from .filters import AddContextualFieldFilter, MaskPasswordsInLogs
from .formatters import JSONFormatter, default_formatter
from .utils import _sanitize_stacktrace_for_json_fields


def _uncaught_exception_logger(
    type: BaseException, exc: Exception, traceback: TracebackException
):
    exception_string = _sanitize_stacktrace_for_json_fields(type, exc, traceback)
    # raise to root logger where it will be consumed by the formatter attached to our handler
    logging.getLogger().error(exception_string)


def configure_logging(
    logger_name: str, level: str, log_format: str = "json"
) -> logging.Logger:
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(level)

    assert logger.hasHandlers()
    for handler in logger.handlers:
        if log_format != "console":
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(default_formatter)
        handler.addFilter(MaskPasswordsInLogs())
        handler.addFilter(AddContextualFieldFilter("service", logger_name))

    sys.excepthook = _uncaught_exception_logger

    return logging.getLogger(logger_name)
