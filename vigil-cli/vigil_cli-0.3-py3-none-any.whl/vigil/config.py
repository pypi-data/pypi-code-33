""" Handle configuration of Vigil."""
# Standard modules
import atexit
import base64
import collections
import logging
import os
import shutil

# External dependencies
import ruamel.yaml
import pkg_resources


log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Config(collections.MutableMapping):
    """
    Class to hold config settings using yaml. Behaves like a dictionary.
    """
    default_config = pkg_resources.resource_filename(
        __name__, 'config/config.yaml')

    def __init__(self, path=None, _parent=None, _config=None):
        self._parent = _parent

        # Use default path to configuration, if none is given
        self._configpath = self.get_configpath(
            path or self._default_configpath())

        if not self._parent:
            self._config = self._load(self._configpath)
        else:
            self._config = _config

        if not self._config['savepath']:
            self._config['savepath'] = self._savepath()

        # Check if password key exists and read its value
        try:
            password = self._config['email']['smtp_password']
            self._config['email']['smtp_password'] = Password.decode(password)
        except KeyError:
            password = None

        # Save the config file on exit
        atexit.register(self.save)

    @staticmethod
    def _savepath():
        """
        Create a file to hold the collection data if necessary and return
        the path.

        Returns:
            Savepath for holding collection data.
        """
        # If environment is not set, fall back to default path.
        default = os.path.expanduser('~/.local/share/vigil/watches.json')
        savepath = os.getenv('XDG_DATA_HOME', default)
        log.debug('savepath=%s', savepath)
        return savepath

    def get_configpath(self, configpath):
        """
        Create configuration file is necessary and return the path.

        Args:
            configpath (str): Path to configuration file.

        Returns:
            str: Path to configuration file.
        """
        # Use default config if it doesn't exists.
        if not os.path.isfile(configpath):
            self._create_config(configpath)
        return configpath

    @staticmethod
    def _default_configpath():
        """
        Get the default confipath for the environment.

        Returns:
            Path to the config file.
        """
        # If environment is not set, fall back to default path.
        default = os.path.expanduser('~/.config/vigil/config.yaml')
        configpath = os.getenv('XDG_CONFIG_HOME', default)
        log.debug('configpath=%s', configpath)

        return configpath

    @staticmethod
    def _create_config(configpath):
        """
        Create default config in the config path.
        """
        configdir = os.path.dirname(configpath)

        try:
            log.debug('Create directory directory=%s', configdir)
            os.makedirs(configdir)
        except FileExistsError:
            log.debug('Directory already exists directory=%s', configdir)

        log.debug('Copy: src=%s dest=%s', Config.default_config, configpath)
        shutil.copy(Config.default_config, configpath)

    def email_configured(self):
        """
        Check if email is properly configured.

        Returns:
            bool: True of email settings are configured, false otherwise.
        """
        default_config = self._load(Config.default_config)
        return self._config['email'] != default_config['email']

    @staticmethod
    def _load(path):
        """
        Load configuration saved in given path.

        Args:
            path (str): Path to the configuration file.

        Returns:
            dict: Dictionary of configuration values.
        """
        with open(path, encoding='utf-8') as file_:
            log.debug('Open: file=%s', file_)
            return ruamel.yaml.load(file_.read(), ruamel.yaml.RoundTripLoader)

    def save(self):
        """
        Save the configuration.
        """
        if self._parent:
            self._parent.save()
        else:
            with open(self._configpath, 'w', encoding='utf-8') as file_:
                log.debug('Open file=%s', file_)
                self._config['email']['smtp_password'] = Password.encode(
                    self._config['email']['smtp_password'])
                ruamel.yaml.dump(
                    self._config, file_, Dumper=ruamel.yaml.RoundTripDumper)

    def _as_config(self, dict_):
        """
        Save config inside config.
        """
        if isinstance(dict_, collections.MutableMapping):
            return Config(_parent=self, _config=dict_)
        return dict_

    def __getitem__(self, item):
        if item not in self._config:
            raise KeyError(item)
        return self._config[item]

    def __setitem__(self, key, value):
        self._config[key] = self._as_config(value)
        self.save()

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __setattr__(self, attr, value):
        if attr.startswith("_"):
            self.__dict__[attr] = value
        else:
            self.__setitem__(attr, value)

    def __delitem__(self, key):
        del self._config[key]

    def __iter__(self):
        for item in self._config:
            yield item

    def __len__(self):
        return len(self._config)

    def __repr__(self):
        return repr(self._config)


class Password:
    """
    Represents a password.

    Attributes:
        encoded (str): Encoded version of password.
        decoded (str): Decoded version of password.
    """

    def __init__(self, password):
        if self._is_encoded(password):
            self.encoded = password
            self.decoded = self._from_b64(password)
        else:
            self.encoded = self._to_b64(password)
            self.decoded = password

    @staticmethod
    def _is_encoded(string):
        """
        Check if string is encoded in Base64.

        Args:
            string (str): String to check.

        Returns:
            bool: True if string is encoded in base64, false otherwise.
        """
        return string[0] == '{' and string[-1] == '}'

    @staticmethod
    def _to_b64(password):
        """
        Encode password to Base64.

        Args:
            password (str): Password in plaintext.

        Returns:
            str: Password in Base64.
        """
        # Change to bytes
        password = password.encode('utf-8')
        # Encode to Base64 and add brackets
        return '{' + base64.b64encode(password).decode('utf-8') + '}'

    @staticmethod
    def _from_b64(password):
        """
        Decode password from Base64.

        Args:
            password (str): Base64 encoded password.

        Returns:
            str: Password in plaintext.
        """
        # Remove the brackets and change to bytes
        password = password[1:-1].encode('utf-8')
        return base64.b64decode(password).decode('utf-8')

    @classmethod
    def encode(cls, password):
        """
        Encode a password.

        Args:
            password (str): Unencoded password.

        Returns:
            str: Encoded password.
        """
        return cls(password).encoded

    @classmethod
    def decode(cls, password):
        """
        Decode a password.

        Args:
            password (str): Encoded password.

        Returns:
            str: Decoded password.
        """
        return cls(password).decoded
