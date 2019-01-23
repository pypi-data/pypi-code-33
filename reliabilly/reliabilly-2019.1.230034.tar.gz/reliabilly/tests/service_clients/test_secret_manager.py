from unittest import TestCase, skipUnless
from unittest.mock import MagicMock
from reliabilly.settings import Constants, Settings
from reliabilly.components.tools.secret_manager import SecretManager


class SecretManagerTests(TestCase):
    def test_get_secret(self):
        mock = MagicMock()
        expected_value = 'test_secret_value'
        mock.get_secret_value.return_value = {'SecretString': expected_value}
        manager = SecretManager(mock, mock)
        actual = manager.get_secret('test')
        self.assertEqual(expected_value, actual)

    def test_get_secret_no_attribute(self):
        mock = MagicMock()
        manager = SecretManager(mock, mock)
        mock.get_secret_value.side_effect = Exception
        result = manager.get_secret('test')
        self.assertIsNone(result)
        mock.error.assert_called_once()

    @skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
    def test_real_secret(self):
        manager = SecretManager()
        value = manager.get_secret('reliabilly.developer_keys')
        self.assertEqual(value, 'REPLACE_WITH_EXPECTED')
