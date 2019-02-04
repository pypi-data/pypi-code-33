import os
import logging
import requests
from py_spring_config.exceptions import AutoConfigurationFailedException

def _load_properties(spring_config_url, app_name, profile="*"):
    logger = logging.getLogger()

    if not app_name:
        logger.error("APP_NAME was not provided")
        raise AutoConfigurationFailedException()

    if not spring_config_url:
        logger.error("CONFIG_SERVER was not provided")
        raise AutoConfigurationFailedException()

    logger.info("Auto configuring, from config server %s",
                spring_config_url)

    connect_string = "/".join((spring_config_url, app_name, profile if profile else "*"))

    properties = requests.get(connect_string).json()

    loaded_properties = properties.get("propertySources")
    error = properties.get("error")
    message = properties.get("message")

    if error and message:
        logger.error("Error loading config: %s", message)
        raise AutoConfigurationFailedException()

    return loaded_properties[0]["source"]

def load(obj, env='production', silent=False, key=None, filename=None):
    """
    Reads and loads in to "obj" a single key or all keys from source
    :param obj: the settings instance
    :param env: settings current env default='development'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :param filename: Custom filename to load
    :return: None
    """
    # Load data from your custom data source (file, database, memory etc)
    # use `obj.set` or `obj.update` to include the data in dynaconf
    CONFIG_SERVER = os.getenv('CONFIG_SERVER')
    APP_NAME = os.getenv('APP_NAME')
    PROFILE = os.getenv('PROFILE')

    props = _load_properties(CONFIG_SERVER, APP_NAME, PROFILE)
    for k, v in props.items():
        obj.set(k.replace(".", "_"), v)
