"""
Functions and classes for taking commandline arguments and forming an
object which will give you a set of FattoushConfig objects, each of
which contains all the information necessary to run lettuce against a
specified webdriver configuration, whither in saucelabs or local.
"""
import json
from multiprocessing import Process
from os import environ, path
from lettuce import world
from ..runner.parsing import parse_args
import urlparse
from jsonschema import validate
from .config import FattoushConfig


class FattoushConfigGroup(object):

    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "schema for a single file fattoush config",

        "type": "object",
        "required": ["browsers"],
        "properties": {
            "description": {"$ref": "#/definitions/comment"},
            "server": {
                "anyOf": [
                    {"$ref": "#/definitions/saucelabs"},
                    {"$ref": "#/definitions/local"}
                ]
            },
            "browsers": {
                "type": "array",
                "minItems": 1,
                "items": {"$ref": "#/definitions/browser"},
                "uniqueItems": True
            }
        },
        "definitions": {
            "comment": {
                "description":
                    "Not used anywhere, just a comment, has no validation, "
                    "so you can store anything, intended to allow strings, "
                    "and lists of strings, in order to facilitate multi-line "
                    "comments, but could take an object with all sorts "
                    "of meta-data... Please don't abuse."
            },
            "saucelabs": {
                "description": "Specification of how to connect to saucelabs",
                "properties": {
                    "description": {"$ref": "#/definitions/comment"},
                    "url": {
                        "description":
                            "The initial URL to load when the test begins",
                        "type": "string"
                    },
                    "user": {
                        "description":
                            "The user name used to invoke Sauce OnDemand",
                        "type": "string"
                    },
                    "key": {
                        "description":
                            "The access key for the user used to invoke "
                            "Sauce OnDemand",
                        "type": "string"
                    }
                },
                "required": ["user", "key"],
                "additionalProperties": False
            },
            "local": {
                "description":
                    "Specification of how to connect to a selenium server on "
                    "your local network. Defaults to 127.0.0.1:4444",
                "properties": {
                    "description": {"$ref": "#/definitions/comment"},
                    "host": {
                        "description": "The hostname of the Selenium server",
                        "type": "string"
                    },
                    "port": {
                        "description": "The port of the Selenium server",
                        "type": "string"
                    },
                    "url": {
                        "description":
                            "The initial URL to load when the test begins",
                        "type": "string"
                    }
                },
                "additionalProperties": False
            },
            "browser": {
                "description":
                    "Specification of the desired capabilities to "
                    "give webdriver",
                "type": "object",
                "properties": {
                    "description": {"$ref": "#/definitions/comment"},
                    "platform": {"type": "string"},
                    "os": {"type": "string"},
                    "browser": {
                        "type": "string",
                        "enum": list(FattoushConfig.desired.keys()),
                    },
                    "url": {
                        "type": "string",
                        "description":
                            "Contains the operating system, version and "
                            "browser name of the selected browser, in a "
                            "format designed for use by the Selenium "
                            "Client Factory"
                    },
                    "browser-version": {"type": "string"}
                },
                "required": ["browser"]
            }
        }
    }

    @staticmethod
    def config_from_env():
        """
        Joyfully SauceConnect presents completely different
        environmental variables based on whether you are
        running against one saucelabs session or several.

        This function will return a list of different session
        configurations whatever the case - empty if there are
        none, a list with only one item if there is only one,
        or a list of multiple items if there are many. It's
        almost as if this would have been the sensible way
        for them to do it too.

        The only part which is different in the singular case is
        the missing 'os' key.

        in the multiple case the json string is documented to be
        of the format as follows:

        [
            {
                "platform":"LINUX",
                "os":"Linux",
                "browser":"firefox",
                "url":"sauce-ondemand:?os=Linux&
                                       browser=firefox&
                                       browser-version=16",
                "browser-version":"16"
            },
            {
                "platform":"VISTA",
                "os":"Windows 2008",
                "browser":"iexploreproxy",
                "url":"sauce-ondemand:?os=Windows 2008&
                                       browser=iexploreproxy&
                                       browser-version=9",
                "browser-version":"9"
            }
        ]
        """

        try:
            json_data = environ.get("SAUCE_ONDEMAND_BROWSERS")
            browsers = json.loads(json_data)
        except (ValueError, TypeError):
            url = environ.get("SELENIUM_DRIVER")
            try:
                query = urlparse.urlparse(url).query
                parsed = urlparse.parse_qs(query)
            except AttributeError:
                parsed = {}
            browsers = [
                {
                    "platform": environ.get("SELENIUM_PLATFORM"),
                    "browser": environ.get("SELENIUM_BROWSER"),
                    "url": url,
                    "browser-version": environ.get("SELENIUM_VERSION")
                }
            ]
            if "os" in parsed:
                browsers[0]["os"] = parsed["os"]

        return {
            "server": {
                "host": environ.get("SELENIUM_HOST"),
                "port": environ.get("SELENIUM_PORT"),
                "url": environ.get("SELENIUM_URL"),
                "user": environ.get("SAUCE_USER_NAME"),
                "key": environ.get("SAUCE_API_KEY")
            },
            "browsers": browsers
        }

    @staticmethod
    def config_from_file(absolute_file_path):
        """ Supports reading config a single json file. """
        return json.load(open(absolute_file_path))

    @property
    def xrange(self):
        return xrange(len(self.configs["browsers"]))

    @classmethod
    def from_cli_args(cls):
        import sys
        options = parse_args(sys.argv[1:])
        return cls(options)

    def __init__(self, options):
        """
        Takes the options that are passed into the runner and
        creates a config object that can be referred to throughout
        fattoush.

        :param options: Namespace
        """
        if options.print_schema:
            print(json.dumps(self.schema, indent=2, sort_keys=True))
            exit(0)
        elif options.print_config:
            file_name = path.join(path.dirname(__file__),
                                  'example_config.json')
            with open(file_name) as example:
                print example.read()
            exit(0)

        self._raw_options = options
        self.parallel = options.parallel

        if options.config is None:
            self.configs = self.config_from_env()
        else:
            self.configs = self.config_from_file(options.config)

        validate(self.configs, self.schema)

        xunit_filename = ('lettucetests.xml'
                          if options.enable_xunit
                          and options.xunit_file is None
                          else options.xunit_file)

        self.lettuce_options = {
            'base_path': options.base_path,
            'scenarios': options.scenarios,
            'verbosity': options.verbosity,
            'random': options.random,
            'enable_xunit': options.enable_xunit,
            'xunit_filename': xunit_filename,
            'failfast': options.failfast,
            'auto_pdb': options.auto_pdb,
            'tags': ([tag.strip('@') for tag in options.tags]
                     if options.tags else None)
        }

    @property
    def to_dict(self):
        """
        The returned dictionary gives a shallow copy of the data
        required to create a FeatureConfig.
        """
        return {
            'lettuce_options': self.lettuce_options.copy(),
            'config': self.configs.copy()
        }

    def run(self):
        if not self.configs:
            raise IndexError('There are no webdriver configs against '
                             'which to run lettuce.')

        if self.parallel == 'webdriver':
            self._run_parallel()
        else:
            self._run_series()

    def _run_series(self):
        """
        Runs lettuce against each browser configuration one at a time

        :param self: fattoush.config.FattoushConfigGroup
        """
        ex = None
        results = []

        server = self.configs.get("server", {})
        lettuce = self.lettuce_options
        browsers = self.configs["browsers"]

        for (index, browser) in enumerate(browsers):
            try:
                r = run_single(index=index,
                               browser=browser.copy(),
                               server=server.copy(),
                               lettuce=lettuce.copy())
                results.append(r)
            except BaseException as ex:
                print ex
        if ex is not None:
            raise
        return results

    def _run_parallel(self):
        """
        Runs lettuce against all the browser configurations at the same
        time in different processes.

        :param self: fattoush.config.FattoushConfigGroup
        """
        processes = []

        server = self.configs.get("server", {})
        lettuce = self.lettuce_options
        browsers = self.configs["browsers"]

        for (index, browser) in enumerate(browsers):
            process = Process(None, run_single,
                              kwargs=dict(index=index,
                                          browser=browser,
                                          server=server,
                                          lettuce=lettuce))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()


def run_single(index, browser, server, lettuce):
    """
    :param index: int
    :param browser: dict
    :param server: dict
    :param lettuce: dict
    """

    fattoush_config = FattoushConfig(index=index,
                                     browser=browser,
                                     server=server,
                                     lettuce=lettuce)
    world.absorb(fattoush_config, 'fattoush')
    try:
        result = fattoush_config.run()
        return result
    finally:
        world.spew('fattoush')
