import json
import os
import unittest
from unittest import mock
import requests_mock
from dynaconf.utils import DynaconfDict
from py_spring_config.loader import _load_properties, load
import py_spring_config.exceptions as ex

CONFIG_URL = 'http://springconfig.service.internal'
PROFILE = "master"
APP_NAME = "myapp"

class TestLoadProperties(unittest.TestCase):
    def test_missing_app_name_raises_exception(self):
        with self.assertRaises(ex.AutoConfigurationFailedException):
            _load_properties(CONFIG_URL, None, PROFILE)

    def test_missing_config_server_raises_exception(self):
        with self.assertRaises(ex.AutoConfigurationFailedException):
            _load_properties(None, APP_NAME, PROFILE)

    @requests_mock.mock()
    def test_error_response_raises_exception(self, m):
        print(os.getcwd())
        config_response = _load_file("py_spring_config/tests/fixtures/fixture_failure.json")
        m.get("/".join((CONFIG_URL, APP_NAME, PROFILE)), json=config_response)
        with self.assertRaises(ex.AutoConfigurationFailedException):
            _load_properties(CONFIG_URL, APP_NAME, PROFILE)

    @requests_mock.mock()
    def test_success_response_returns_correct_config_dictionary(self, m):
        config_response = _load_file("py_spring_config/tests/fixtures/fixture_success.json")
        m.get("/".join((CONFIG_URL, APP_NAME, PROFILE)), json=config_response)
        config_dict = _load_properties(CONFIG_URL, APP_NAME, PROFILE)
        self.assertEqual(7, len(config_dict.keys()))
        self.assertEqual(config_dict["logging.level.root"], "INFO")

class TestLoad(unittest.TestCase):
    @requests_mock.mock()
    @mock.patch.dict("os.environ", {'CONFIG_SERVER': CONFIG_URL, 'APP_NAME': APP_NAME, 'PROFILE': PROFILE})
    def test_loader_sets_dynaconf_values_with_correct_keys(self, m):
        mocked_settings = DynaconfDict()
        config_response = _load_file("py_spring_config/tests/fixtures/fixture_success.json")
        m.get("/".join((CONFIG_URL, APP_NAME, PROFILE)), json=config_response)
        load(mocked_settings)
        self.assertEqual(mocked_settings["logging_level_root"], "INFO")

def _load_file(filename):
    with open(filename, "r") as f:
        return json.load(f)

if __name__ == '__main__':
    unittest.main()
