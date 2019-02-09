""" Handle logging."""
# Standard modules
import os
import logging.config

# External dependencies
import ruamel.yaml
import pkg_resources


LOGGER_CONFIG = pkg_resources.resource_filename(
    __name__, '../config/logging.yaml')


def setup_logging(
        default_path=LOGGER_CONFIG,
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """
    Setup logging configuration.
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as file_:
            config = ruamel.yaml.load(
                file_.read(), ruamel.yaml.RoundTripLoader)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
