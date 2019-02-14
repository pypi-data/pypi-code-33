"""
Functions and classes for taking commandline arguments and forming an
object which will give you a set of FattoushConfig objects, each of
which contains all the information necessary to run lettuce against a
specified webdriver configuration, whither in saucelabs or local.
"""
import copy
import json
import multiprocessing
import urlparse
from os import environ, path

from jsonschema import validate

from fattoush import namespace, util
from fattoush.config import config, deprecated
from fattoush.runner.parsing import parse_args


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
                "anyOf": [
                    {"$ref": "#/definitions/browsers"},
                    {"$ref": "#/definitions/browsers-pre-0.4"}
                ]
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
            "browsers-pre-0.4": {
                "type": "array",
                "minItems": 1,
                "items": {"$ref": "#/definitions/capabilities"},
                "uniqueItems": True,
            },
            "browsers": {
                "description":
                    "Specification of the browsers to ask webdriver to open",
                "type": "object",
                "properties": {
                    "capabilities": {
                        "description":
                            "Keyed lookup of desired capabilities",
                        "type": "object",
                        "additionalProperties": {
                            "$ref": "#/definitions/capabilities",
                        },
                    },
                    "options": {
                        "description":
                            "Keyed lookup of browser options",
                        "type": "object",
                        "additionalProperties": {
                            "$ref": "#/definitions/options",
                        },
                    },
                    "selection": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/browser"},
                    },
                },
                "required": ["selection"],
            },
            "capabilities": {
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
                        "enum": list(config.FattoushConfig.desired.keys()),
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
            },
            "options": {
                "description":
                    "Specification of the browser options to give webdriver",
                "type": "array",
                "items": {"type": "string"},
            },
            "browser": {
                "description":
                    "Specification of a browsers to ask webdriver to open",
                "type": "object",
                "properties": {
                    "description": {"$ref": "#/definitions/comment"},
                    "capabilities": {
                        "anyOf": [
                            {"$ref": "#/definitions/capabilities"},
                            {
                                "type": "string",
                                "description": "Key within capabilities",
                            },
                        ]
                    },
                    "options": {
                        "anyOf": [
                            {"$ref": "#/definitions/options"},
                            {
                                "type": "string",
                                "description": "Key within options",
                            },
                        ]
                    },
                },
            },
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

        :type options: Namespace
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

        self._convert_legacy_config()

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

    def _convert_legacy_config(self):
        if isinstance(self.configs['browsers'], list):
            # Before version 0.4 all capabilities went
            # straight in the browser objects, since 0.4 this
            # has become nested to also include options to set
            # on the remote executor. The pre-0.4 format shall
            # be deprecated from 0.5 onwards.
            with deprecated.FromVersion('0.5', 'Legacy browser config format'):

                browsers = self.configs["browsers"]

                self.configs["browsers"] = {
                    'selection': [
                        {'capabilities': browser} for browser in browsers
                    ]
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

        runner = (
            self._run_parallel if self.parallel == 'webdriver' else
            self._run_series
        )

        return sum(
            result.scenarios_ran - result.scenarios_passed
            for result in runner()
            if result.features_passed < result.features_ran
        )

    def _run_series(self):
        """
        Runs lettuce against each browser configuration one at a time

        :type self: fattoush.config.FattoushConfigGroup
        """
        return list(
            util.try_map(
                _run_kwargs,
                self._iter_browser_kwargs(),
            )
        )

    def _run_parallel(self):
        """
        Runs lettuce against all the browser configurations at the same
        time in different processes.

        :type self: fattoush.config.FattoushConfigGroup
        """
        multiprocessing.Pool().map(
            _run_kwargs,
            self._iter_browser_kwargs(),
        )

    def _iter_browser_kwargs(self):
        browsers = self.configs["browsers"]

        kwargs = {
            'server': self.configs.get("server", {}),
            'lettuce': self.lettuce_options,
        }

        for (index, browser) in enumerate(browsers['selection']):

            kwargs['index'] = index

            caps = browser.setdefault('capabilities', {})
            if not isinstance(caps, dict):
                browser['capabilities'] = browsers['capabilities'][caps]

            opts = browser.setdefault('options', [])
            if not isinstance(opts, list):
                browser['options'] = browsers['options'][opts]

            kwargs['browser'] = browser

            yield kwargs


def _run_kwargs(kwargs):
    """ This would be a starmap in py3... """
    return run_single(**copy.deepcopy(kwargs))


def run_single(index, browser, server, lettuce):
    """
    :type index: int
    :type browser: dict
    :type server: dict
    :type lettuce: dict
    """

    fattoush_config = config.FattoushConfig(
        index=index,
        browser=browser,
        server=server,
        lettuce_cfg=lettuce,
    )
    namespace.config = fattoush_config

    try:
        result = fattoush_config.run()
        return result
    finally:
        namespace.config = None
