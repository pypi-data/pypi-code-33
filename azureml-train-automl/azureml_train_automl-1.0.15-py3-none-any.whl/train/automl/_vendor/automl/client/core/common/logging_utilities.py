"""Utility module for logging."""
import contextlib
import logging
import logging.handlers as handlers
import threading
import traceback
import uuid

from datetime import datetime

from .constants import TelemetryConstants
from .exceptions import AutoMLException, ErrorTypes

# import telemetry package if available.
try:
    from azureml.telemetry import get_telemetry_log_handler
    from azureml.telemetry.logging_handler import AppInsightsLoggingHandler

    telemetry_imported = True
except ImportError:
    telemetry_imported = False


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

    message = [
        'An exception was raised.',
        'Exception Message: {}'.format(exception),
        '{}'.format(traceback.format_exc())
    ]
    custom_dimensions = {}
    if isinstance(exception, AutoMLException):
        custom_dimensions['error_type'] = exception.error_type
    else:
        custom_dimensions['error_type'] = ErrorTypes.Unclassified
    logger.error('\n'.join(message), extra={'properties': custom_dimensions})


def get_logger(namespace=None, filename=None, verbosity=logging.DEBUG, extra_handlers=None,
               component_name=None):
    """
    Create the logger with telemetry hook.

    :param namespace: The namespace for the logger
    :param filename: log file name
    :param verbosity: logging verbosity
    :param extra_handlers: any extra handlers to attach to the logger
    :param component_name: component name
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

        if telemetry_imported:
            if not _found_handler(logger, AppInsightsLoggingHandler):
                logger.addHandler(get_telemetry_log_handler(component_name=component_name))

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


BLACKLISTED_LOGGING_KEYS = ['path', 'resource_group', 'workspace_name', 'data_script', 'debug_log']


def log_system_info(logger, prefix_message=None):
    """
    Log cpu, memory and OS info.

    :param logger: logger object
    :param prefix_message: string that in the prefix in the log
    :return: None
    """
    if prefix_message is None:
        prefix_message = ''

    try:
        import psutil
        logger.info("{}CPU logical cores: {}, CPU cores: {}, virtual memory: {}, swap memory: {}.".format(
            prefix_message,
            psutil.cpu_count(), psutil.cpu_count(logical=False),
            psutil.virtual_memory().total, psutil.swap_memory().total)
        )
    except ImportError:
        logger.warning("psutil not found, skipping logging cpu and memory")

    import platform
    logger.info("{}Platform information: {}.".format(prefix_message, platform.platform()))


def _found_handler(logger, handle_name):
    """
    Check logger with the given handler and return the found status.

    :param logger: Logger
    :param handle_name: handler name
    :return: boolean: True if found else False
    """
    for log_handler in logger.handlers:
        if isinstance(log_handler, handle_name):
            return True

    return False


@contextlib.contextmanager
def log_activity(logger, activity_name=None, activity_type=None, custom_dimensions=None):
    """
    Log the activity status with duration.

    :param logger: logger
    :param activity_name: activity name
    :param activity_type: activity type
    :param custom_dimensions: custom dimensions
    """
    activity_info = dict(activity_id=str(uuid.uuid4()), activity_name=activity_name, activity_type=activity_type)

    properties = dict()
    custom_dimensions = custom_dimensions or {}
    activity_info.update(custom_dimensions)
    properties['properties'] = activity_info

    completion_status = TelemetryConstants.SUCCESS

    start_time = datetime.utcnow()
    logger.info("ActivityStarted: {}".format(activity_name), extra=properties)

    try:
        yield
    except Exception:
        completion_status = TelemetryConstants.FAILURE
        raise
    finally:
        end_time = datetime.utcnow()
        duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)
        activity_info["durationMs"] = duration_ms
        activity_info["completionStatus"] = completion_status

        logger.info("ActivityCompleted: Activity={}, HowEnded={}, Duration={}[ms]".
                    format(activity_name, completion_status, duration_ms), extra=properties)


class LogConfig:
    """
    Class containing the information needed to create a new logger.

    The Python logger is not serializable, so passing this data is sufficient to recreate a logger in a subprocess
    where all arguments must be serializable.
    """

    def __init__(self, log_filename, log_verbosity, log_namespace):
        """
        Construct a LogConfig object.

        :param log_filename: name of the log file
        :param log_verbosity: the logging verbosity level
        :param log_namespace: the logging namespace
        """
        self._log_filename = log_filename
        self._log_verbosity = log_verbosity
        self._log_namespace = log_namespace

    def get_params(self):
        """Get the logging params."""
        return self._log_filename, self._log_verbosity, self._log_namespace

    def get_filename(self):
        """Get the log filename."""
        return self._log_filename

    def get_namespace(self):
        """Get the log namespace."""
        return self._log_namespace

    def get_verbosity(self):
        """Get the log verbosity."""
        return self._log_verbosity

    def get_component_name(self):
        """Get the component name."""
        return TelemetryConstants.COMPONENT_NAME
