"""
Functions for putting together sauce configuration,
be it from environmental variables or from a JSON string.
"""
import json

from os import path

import lettuce
import selenium.webdriver

import fattoush.util


class FattoushConfig(object):
    _capabilities = None

    @fattoush.util.flatmap(selenium.webdriver.DesiredCapabilities, to_cls=dict)
    def desired(cap_name, cap):
        """
        :type cap_name:    str
        :type cap:         str
        """
        if isinstance(cap, dict):
            browser_name = cap.get("browserName")

            if browser_name is not None:

                cap_name_lower = cap_name.lower()

                yield cap_name_lower, cap

                if (
                    cap_name_lower != browser_name and
                    cap_name_lower == browser_name.lower
                ):
                    yield browser_name, cap

    desired.update({
        "googlechrome": selenium.webdriver.DesiredCapabilities.CHROME,
        "phantom": selenium.webdriver.DesiredCapabilities.PHANTOMJS,
        "iexploreproxy": selenium.webdriver.DesiredCapabilities.INTERNETEXPLORER,
    })

    @fattoush.util.flatmap(selenium.webdriver, to_cls=dict)
    def _options(_, cls):
        try:
            if cls.__name__ == 'Options':
                option = cls()

                yield option.capabilities["browserName"], cls
        except (NameError, KeyError):
            pass

    def _augment_xunit_filename(self):
        index = self.index
        xunit_file = self.run_args['xunit_filename']

        if xunit_file is None:
            return

        if '.' in path.basename(xunit_file):
            prefix, suffix = path.splitext(xunit_file)
            xunit_file = '{0}_{1}.{2}'.format(prefix, index, suffix)
        else:
            xunit_file = '{0}_{1}'.format(xunit_file, index)
        self.run_args['xunit_filename'] = xunit_file

    def _augment_server(self):
        if self.server is None:
            self.server = {}
        server = self.server
        if "host" not in server:
            server[u"host"] = ("127.0.0.1" if "user" not in server
                               else "ondemand.saucelabs.com")
        if "port" not in server:
            server[u"port"] = ("4444" if "user" not in server
                               else "80")
        if "url" in server and not server["url"]:
            del server["url"]

    def run(self):
        try:
            return lettuce.Runner(**self.run_args).run()
        except BaseException:
            print "Lettuce raised the following exception:"
            raise

    def _augment_browser(self):
        """
        All parts of the browser config must be a string except for the
        description, which can hold any format.
        """

        def to_string(obj):
            try:
                if isinstance(obj, unicode):
                    return obj
                elif isinstance(obj, list):
                    return ''.join(obj)
            except TypeError:
                return json.dumps(obj)

        if "description" in self.browser:
            self.browser["description"] = to_string(
                self.browser["description"])

    def __init__(self, index, browser, server, lettuce_cfg):
        """
        :type index: int
        :type browser: dict
        :type server: dict
        :type lettuce_cfg: dict
        """
        self.index = index
        self.server = server
        self.browser = browser.copy()
        self.run_args = lettuce_cfg

        self._augment_xunit_filename()
        self._augment_server()

        self._augment_browser()
        self.name = _create_name_from_capabilities(
            self.browser['capabilities'],
            surround=False,
        )

    @property
    def command_executor(self):
        host = self.server["host"].rstrip('/')

        try:
            protocol, host = host.split("://")
        except ValueError:
            protocol = 'http'

        try:
            host, url_path = host.split(":")
        except ValueError:
            port = self.server["port"]
        else:
            split_path = url_path.split("/")
            port = split_path[0]
            split_path[0] = host
            host = '/'.join(split_path)

        split_path = host.split('/')
        host, split_path = split_path[0], split_path[1:]

        endpoint = "/".join(split_path) if split_path else "wd/hub"

        if "user" in self.server and "key" in self.server:
            return ('{protocol}://{user}:{key}@{host}:{port}/{endpoint}'
                    ).format(protocol=protocol,
                             user=self.server["user"],
                             key=self.server["key"],
                             host=host,
                             port=port,
                             endpoint=endpoint)

        elif "user" in self.server:
            return ('{protocol}://{user}@{host}:{port}/{endpoint}'
                    ).format(protocol=protocol,
                             user=self.server["user"],
                             host=host,
                             port=port,
                             endpoint=endpoint)
        else:
            return ('{protocol}://{host}:{port}/{endpoint}'
                    ).format(protocol=protocol,
                             host=host,
                             port=port,
                             endpoint=endpoint)

    @property
    def base_capabilities(self):
        browser_name = self.browser['capabilities']["browser"]

        return self.desired.get(
            browser_name,
            selenium.webdriver.DesiredCapabilities.CHROME
        )

    def desired_capabilities(self, name):
        capabilities = self.base_capabilities.copy()

        capabilities.update({
            k: v for k, v in self.browser['capabilities'].items()
            if k != "browser"
        })

        capabilities["name"] = name

        return capabilities

    def options(self):
        browser_name = self.base_capabilities["browserName"]

        cls = self._options.get(browser_name)

        if cls is not None:

            browser_options = cls()

            for option in self.browser['options']:
                browser_options.add_argument(option)

            return browser_options


def _create_name_from_capabilities(caps, surround=True):
    if isinstance(caps, (str, unicode)):
        return caps

    if hasattr(caps, 'iteritems'):
        return _do_join(
            parts=_mapping_to_name_parts(caps),
            surround=surround
        )
    elif hasattr(caps, '__iter__'):
        return _do_join(
            parts=_iterable_to_name_parts(caps),
            surround=surround
        )

    return repr(caps)


def _mapping_to_name_parts(caps):
    for key, value in sorted(caps.items()):
        if key == 'description':
            continue

        yield '='.join((key, _create_name_from_capabilities(value)))


def _iterable_to_name_parts(caps):
    for value in caps:
        yield _create_name_from_capabilities(value)


def _do_join(parts, surround, with_=';'):
    whole = with_.join(parts)

    if surround:
        whole = '{{{}}}'.format(whole)

    return whole
