## Configuration class
## Update parameters using command line args

from ConfigParser import SafeConfigParser
import os
import errno

class Config(object):
    def __init__(self):
        self._parser = SafeConfigParser({"OPENFIN-API-KEY": "",
                                   "BASE-URL": "https://log-manager.openfin.co/api/v1/",
                                   "PRIVATE-KEY-FILE": ""})

        home_dir = os.path.expanduser("~")
        self._config_file = os.path.join(home_dir, ".openfin", "config.ini")
        self._parser.read(self._config_file)

        self._api_key = self._parser.get("DEFAULT", "OPENFIN-API-KEY")
        self._base_url = self._parser.get("DEFAULT", "BASE-URL")
        self._headers = {"X-Openfin-Api-Key": self.api_key}
        self._private_key = self._parser.get("DEFAULT", "PRIVATE-KEY-FILE")

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, value):
        self._base_url = value

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, kv_pair):
        if not isinstance(kv_pair, tuple) or len(kv_pair) != 2:
            return

        key = kv_pair[0]
        value = kv_pair[1]
        if key in self._headers:
            del self._headers[key]
        self._headers[key] = value

    @property
    def private_key(self):
        return self._private_key

    @private_key.setter
    def private_key(self, value):
        self._private_key = value

    def save(self):
        """
        Saves the state of the config to the config file.
        """
        self._parser.set("DEFAULT", "BASE-URL", self._base_url)
        self._parser.set("DEFAULT", "OPENFIN-API-KEY", self._api_key)
        self._parser.set("DEFAULT", "PRIVATE-KEY-FILE", self._private_key)

        if not os.path.exists(os.path.dirname(self._config_file)):
            try:
                os.makedirs(os.path.dirname(self._config_file))
            except OSError as exc: 
                # In case file gets created in between .exists() and .makedirs() calls, this will get thrown
                if exc.errno != errno.EEXIST:
                    raise

        with open(self._config_file, "w") as cfg_file:
            self._parser.write(cfg_file)

