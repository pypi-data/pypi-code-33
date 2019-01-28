import json

from colorama import init, deinit
from pprint import pprint

from api_generator import load
from argus_cli.settings import settings, update_settings  # Settings has to be before the logger!
from argus_cli.helpers.log import log
from argus_cli.arguments import get_provider_arguments, parse_arguments
from argus_cli.plugin import load_plugin_module, get_plugin_modules


def setup() -> None:
    """Reads program arguments, sets up the API and loads plugins"""
    arguments = get_provider_arguments()
    if arguments.get("apikey"):
        update_settings(["api", "api_key"], arguments["apikey"])

    load(settings["api"]["api_url"], settings["api"]["definitions"])

    plugins = get_plugin_modules(settings["cli"]["plugins"])
    log.info("Loading plugins...")
    for plug in plugins:
        load_plugin_module(plug)


def run() -> None:
    """Parses command and runs the application"""
    command, arguments = parse_arguments()

    log.debug("Running command \"{}\"".format(command))
    result = command(**arguments)

    if isinstance(result, dict):
        print(json.dumps(result, indent=2))
    elif result:
        pprint(result)


def main() -> None:
    """Used to launch the application"""
    # Initialize colorama to enable Windows color support
    init()

    # Initialize and run argus cli
    setup()
    run()

    # Deinitialize colorama
    deinit()
