"""Load default YAML settings file, then look for user defined settings and create a ChainMap."""
import os
from os.path import join, dirname, abspath, expanduser, exists
from yaml import load

from argus_cli.helpers import log as log_module

# Default plugin location
DEFAULT_PLUGIN_DIRECTORY = abspath(join(dirname(abspath(__file__)), "..", "argus_plugins"))

# Default locations for settings.ini files
SETTINGS_ENV_VAR = "ARGUS_CLI_SETTINGS"

# Expected user location if none is provided
DEFAULT_SETTINGS_LOCATION = join(abspath(dirname(__file__)), "resources", "config.yaml")
USER_SETTINGS_LOCATION = os.environ.get(SETTINGS_ENV_VAR, join(expanduser("~"), ".argus_cli.yaml"))

ENVIRONMENT_VARIABLES = {
    "ARGUS_API_KEY": ["api", "api_key"],
    "ARGUS_API_URL": ["api", "api_url"],
}

settings = None


def merge(source: dict, destination: dict) -> dict:
    """Deep merges two dictionaries and replaces values from destination with the ones from source."""
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


def set_dict(d: dict, key, value):
    """Deep-sets a dictionary"""
    if not isinstance(key, list):
        d[key] = value

    current_key = key[0]
    if len(key) > 1:
        return set_dict(d[current_key], key[1:], value)

    d[current_key] = value


def _get_settings() -> dict:
    """Gets settings from file and env-vars

    Env-vars take precedence over the config file
    """
    # Get settings from config file
    settings = merge(
        load(open(USER_SETTINGS_LOCATION)) if exists(USER_SETTINGS_LOCATION) else {},
        load(open(DEFAULT_SETTINGS_LOCATION))
    )

    # Get settings from enviornment
    for env_var, dict_key in ENVIRONMENT_VARIABLES.items():
        value = os.environ.get(env_var)
        if value:
            set_dict(settings, dict_key, value)

    return settings


def _get_plugin_directories(settings: dict) -> dict:
    if "plugins" not in settings["cli"].keys() or not settings["cli"]["plugins"]:
        log_module.log.info("No plugin directory specified. Defaulting to %s" % DEFAULT_PLUGIN_DIRECTORY)
        settings["cli"]["plugins"] = []
    else:
        # Remove plugin directories that don't exist and warn about them

        for directory in settings["cli"]["plugins"]:
            if not exists(directory):
                log_module.log.warning("Plugin directory %s does not exist. Ignoring")

        settings["cli"]["plugins"] = [
            directory
            for directory in settings["cli"]["plugins"]
            if exists(directory)
        ]

    settings["cli"]["plugins"] += [DEFAULT_PLUGIN_DIRECTORY]

    return settings


def _get_debug_mode(settings: dict) -> dict:
    """Sets up debug mode if there is a --debug argument on the commandline"""
    from argus_cli import arguments

    if arguments.get_provider_arguments().get("debug"):
        settings["global"] = {"debug": True}

        for logger in settings["logging"]["handlers"].values():
            logger["level"] = "DEBUG"

        log_module.log.info("Debug mode activated!")

    return settings


def load_settings():
    """Loads settings from a settings-file.

    :param debug_mode: Weather or not to explicity enable debug mode
    """
    global settings
    settings = _get_settings()

    # Get logging settings
    settings = _get_debug_mode(settings)
    # Then configure the logger with these settings
    log_module.setup_logger(settings["logging"])

    # and proceed to get plugin directories
    settings = _get_plugin_directories(settings)

    log_module.log.debug("Loaded settings:\n\t%s" % settings)


def update_settings(key, value):
    global settings
    set_dict(settings, key, value)


load_settings()
