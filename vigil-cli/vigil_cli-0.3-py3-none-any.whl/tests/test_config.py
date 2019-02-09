# Standard modules
import copy
import os
import shutil

# External dependencies
import pytest
import ruamel.yaml

# Local modules
from .context import vigil
from vigil.config import Config, Password


class TestConfig:
    """
    Class for testing config.py.
    """

    def test_load(self, config, nosave):
        """
        Config should load properly.
        """
        assert config['output'] == ['email']
        assert config['email']['from'] == 'from@example.org'
        assert config['email']['to'] == 'to@example.org'
        assert config['email']['smtp_host'] == 'smtp.example.org'
        assert config['email']['smtp_port'] == 465
        assert config['email']['smtp_username'] == 'username'
        assert config['email']['smtp_password'] == 'password'

    def test_honor_xdg_config_home(self, monkeypatch, testfile, nosave):
        """
        XDG_CONFIG_HOME should be preferred when set.
        """
        monkeypatch.setenv('XDG_CONFIG_HOME', testfile)
        shutil.copy('tests/data/sample.yaml', testfile)
        config = Config()
        assert config._default_configpath() == testfile

    def test_default_config_path(self, monkeypatch, nosave):
        """
        Config path should default to vigil/config/config.yaml.
        """
        monkeypatch.delenv('XDG_CONFIG_HOME', raising=False)
        config = Config()
        default = os.path.expanduser('~/.config/vigil/config.yaml')
        assert config._default_configpath() == default

    def test_honor_xdg_data_home(self, config, monkeypatch, tmpdir, nosave):
        """
        XDG_DATA_HOME should be preferred when set.
        """
        monkeypatch.setenv('XDG_DATA_HOME', tmpdir)
        assert config._savepath() == tmpdir

    def test_default_save_path(self, config, monkeypatch, nosave):
        """
        Save path should default to ~/.local/share/vigil/watches.json
        """
        monkeypatch.delenv('XDG_DATA_HOME', raising=False)
        default = os.path.expanduser('~/.local/share/vigil/watches.json')
        assert config._savepath() == default

    def test_save(self, config):
        """
        Config should be saved in the configured path.
        """
        old = config._config
        config.save()

        with open(config._configpath, encoding='utf-8') as f:
            test = ruamel.yaml.load(f.read(), ruamel.yaml.RoundTripLoader)
        assert test == old

    def test_roundabout(self, config, configfile):
        """
        Saving and loading config should not affect the config.
        """
        old = copy.deepcopy(config._config)
        config.save()
        test = Config(configfile)

        assert test == old

    def test_email_configured(self, config, configfile):
        """
        Should return True if email settings differ from the default ones.
        """
        # FIXME Config fixture is saving to system config, messing up tests
        config['savepath'] = None
        config['email']['smtp_password'] = 'password'

        assert not config.email_configured()
        config['email']['from'] = 'new@email.com'
        assert config.email_configured()

    def test__load(self, config):
        """
        Should load config from yaml and return it as dictionary.
        """
        config['savepath'] = None
        loaded = config._load(config._configpath)
        assert loaded == config._config


class TestPassword:
    """
    Test Password class.
    """

    @pytest.fixture
    def encoded(self):
        return '{cGFzc3dvcmQ=}'

    @pytest.fixture
    def unencoded(self):
        return 'password'

    def test__is_encoded(self, encoded, unencoded):
        """
        Should return True for string enclosed in curly brackets.
        """
        assert Password._is_encoded(encoded)
        assert not Password._is_encoded(unencoded)

    def test_encode(self, encoded, unencoded):
        """
        Encodes password to Base64 and wraps in curly brackets.
        """
        assert Password.encode(unencoded) == encoded

    def test_decode(self, encoded, unencoded):
        """
        Remove curly brackets and decode password from Base64.
        """
        assert Password.decode(encoded) == unencoded

    def test_obfuscation_roundabout(self, encoded, unencoded):
        """
        Encoding and decoding password should result in the original password.
        """
        assert Password.decode(Password.encode(unencoded)) == unencoded
