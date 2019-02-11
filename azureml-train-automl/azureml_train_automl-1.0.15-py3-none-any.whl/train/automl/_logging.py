# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Auto ML common logging module."""
import logging

from automl.client.core.common import logging_utilities as log_utils
from azureml.telemetry import AML_INTERNAL_LOGGER_NAMESPACE, get_telemetry_log_handler


_blacklist_logging_keys = ['path', 'resource_group', 'workspace_name', 'data_script',
                           'debug_log']

TELEMETRY_AUTOML_COMPONENT_KEY = 'automl'


def get_logger(log_file_name=None, verbosity=logging.DEBUG):
    """
    Create the logger with telemetry hook.

    :param log_file_name: log file name
    :param verbosity: logging verbosity
    :return logger if log file name is provided otherwise null logger
    :rtype
    """
    telemetry_handler = get_telemetry_log_handler(component_name=TELEMETRY_AUTOML_COMPONENT_KEY)
    logger = log_utils.get_logger(namespace=AML_INTERNAL_LOGGER_NAMESPACE,
                                  filename=log_file_name,
                                  verbosity=verbosity,
                                  extra_handlers=[telemetry_handler])
    return logger


def _log_system_info(logger, prefix_message=None):
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


class LogConfig:
    def __init__(self, log_filename, log_verbosity, log_namespace=None):
        """
        Construct a LogConfig.

        This object holds the information needed to create a new logger.
        The Python logger is not serializable, so passing this data
        is sufficient to recreate a logger in a subprocess where all
        arguments must be serializable.
        """
        self._log_filename = log_filename
        self._log_verbosity = log_verbosity
        if log_namespace is None:
            self._log_namespace = AML_INTERNAL_LOGGER_NAMESPACE
        else:
            self._log_namespace = log_namespace

    def get_params(self):
        """Get the logging params."""
        return (self._log_filename, self._log_verbosity, self._log_namespace)

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
        """Get the component name for telemetry."""
        return TELEMETRY_AUTOML_COMPONENT_KEY
