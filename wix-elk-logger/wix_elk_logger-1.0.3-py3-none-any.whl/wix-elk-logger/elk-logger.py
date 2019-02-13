"""
This package is helper for json formatted logging.
"""

import logmatic
import logging
import os

__all__ = [
    'get_logger'
]


def get_env_var_or_empty(varname: str = None):
    """
    Stubs non existing env vars with empty value
    :param varname: name of env var to get value from
    :return: env vars value or empty string if env var is not defined
    """
    retval = ""
    if varname is not None and varname in os.environ:
        retval = os.environ[varname]
    return retval


def get_logger(service_name: str,
               log_dir_var_name: str = 'APP_LOG_DIR',
               hostname_var_name: str = 'HOSTNAME',
               domain: str = 'default'):
    """
    Creates logger that outputs data to json formatted file with predefined
    fields
    :param service_name: your service name
    :param log_dir_var_name: env var that holds location of logs folder
    :param hostname_var_name: env var that holds hostname value
    :param domain: usually your service runs as part of bigger system. to
    group your messages together set custom domain
    :return:
    """
    logger = logging.getLogger("wix-elk-logger")
    log_dir = get_env_var_or_empty(log_dir_var_name)
    handler = logging.FileHandler(os.path.join(log_dir, service_name + '.log'))
    hostname = get_env_var_or_empty(hostname_var_name)
    handler.setFormatter(logmatic.JsonFormatter(extra={"type": domain,
                                                       "service": service_name,
                                                       "hostname": hostname}))

    logger.addHandler(handler)
    return logger
