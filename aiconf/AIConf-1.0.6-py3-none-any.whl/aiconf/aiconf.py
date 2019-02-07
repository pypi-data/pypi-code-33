import json
import logging
import os

import pyparsing
from pyhocon import ConfigFactory


class ConfigReader:
    """


    Reads and parses the config under the given config.
    Given a default config merges it with the given config (useful when you have a default application config).
    """

    def __init__(self, path=None, default=None):
        """
        Initializes the reader.

        Accepts a config config and a default config config (or resource).

        :param path: Path to the config.
        :param default: fallback config (path, resource or string)
        """
        if path is None:
            path = ""

        if default is None:
            default = ""
        try:
            # is resource
            default = default.decode("utf-8")
        except AttributeError:
            try:
                # is path
                with open(default) as f:
                    default = f.read()
            except FileNotFoundError:
                # let's assume it's just a string (for now)
                pass

        if not path and not default:
            raise ValueError("Either config or fallback must be specified!")
        if path:
            try:
                with open(path, "r") as f:
                    self.config = f.read()

            except FileNotFoundError:
                logging.getLogger(__name__).warning(
                    "{} doesn't exist! will load default only! {}".format(path, os.getcwd()))
                self.config = ""
        else:
            self.config = ""
        self.default = default

    def read_config(self):
        """
        Reads the config and returns a parsed mapping between config keys and (parsed) values.

        If no config is found under config, loads the default config only.

        :return: Mapping from config entries to their parsed values.
        """
        if not self.config:
            return ConfigFactory.parse_string(self.default)
        cfg_str = '{}\n{}'.format(self.default, self.config)

        try:
            return ConfigFactory.parse_string(cfg_str)
        except pyparsing.ParseSyntaxException as e:
            logging.getLogger(__name__).error("Malformed config!:\n{}".format(cfg_str))
            raise ValueError("Malformatted config!") from e


def format_config(config) -> str:
    """
    Formats the config in a more-or-less readable way.

    :class:`ConfigReader`
    :meth:`ConfigReader.read_config`

    :param config: Config to be formatted.
    :return: Formatted config.
    """
    return json.dumps(config.as_plain_ordered_dict(), indent=4)
