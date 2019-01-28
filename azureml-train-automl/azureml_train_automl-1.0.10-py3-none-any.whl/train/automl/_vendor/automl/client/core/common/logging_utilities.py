"""Utility module for logging."""

import logging
import logging.handlers as handlers
import threading
import traceback


file_handlers = {}
file_loggers = {}
log_cache_lock = threading.Lock()


def _get_null_logger(name='null_logger'):
    null_logger = logging.getLogger(name)
    null_logger.addHandler(logging.NullHandler())
    null_logger.propagate = False
    return null_logger


NULL_LOGGER = _get_null_logger()


def log_traceback(exception, logger):
    """
    Log exception traces.

    :param exception: The exception to log.
    :param logger: The logger to use.
    """
    if logger is None:
        logger = NULL_LOGGER

    logger.error(exception)
    logger.error(traceback.format_exc())


def get_logger(namespace=None, filename=None, verbosity=logging.DEBUG, extra_handlers=None):
    """
    Create the logger with telemetry hook.

    :param namespace: The namespace for the logger
    :param log_filename: log file name
    :param verbosity: logging verbosity
    :param extra_handlers: any extra handlers to attach to the logger
    :return: logger if log file name and namespace are provided otherwise null logger
    :rtype
    """
    if filename is None or namespace is None:
        return NULL_LOGGER

    with log_cache_lock:
        if (filename, verbosity) in file_loggers:
            return file_loggers[(filename, verbosity)]

        if filename not in file_handlers:
            handler = handlers.RotatingFileHandler(filename, maxBytes=1000000, backupCount=9)
            log_format = '%(asctime)s - %(levelname)s - %(lineno)d : %(message)s'
            formatter = logging.Formatter(log_format)
            handler.setFormatter(formatter)
            file_handlers[filename] = handler

        logger_name = '%s_%s' % (filename, str(verbosity))
        logger = logging.getLogger(namespace).getChild(logger_name)
        logger.addHandler(file_handlers[filename])
        logger.setLevel(verbosity)

        if extra_handlers is not None:
            for h in extra_handlers:
                logger.addHandler(h)

        logger.propagate = False
        file_loggers[(filename, verbosity)] = logger

        return logger


def cleanup_log_map(log_filename=None, verbosity=logging.DEBUG):
    """
    Cleanup log map.

    :param log_filename: log file name
    :param verbosity: log verbosity
    :return:
    """
    with log_cache_lock:
        logger = file_loggers.pop((log_filename, verbosity), None)
        handler = file_handlers.pop(log_filename, None)
        if handler:
            if logger:
                logger.removeHandler(handler)
            handler.close()
