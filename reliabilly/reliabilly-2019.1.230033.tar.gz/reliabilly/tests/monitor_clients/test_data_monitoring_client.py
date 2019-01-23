# pylint: disable=invalid-name,no-self-use
import unittest
from unittest import skipUnless
from unittest.mock import MagicMock
from reliabilly.components.tools.data_monitoring_client import DataMonitoringClient
from reliabilly.settings import Settings, Constants


class DataMonitoringClientTests(unittest.TestCase):

    def test_generate_payload(self):
        payload = DataMonitoringClient.generate_payload(
            "99", "Updating", "on fire", "http://pipeline.com", "https://fresh.customgit.com")
        expected = {
            "eventType": "ReleaseEvent",
            "environment": "on fire",
            "build_status": "updating",
            "release_number": "99",
            "git_repo": "https://fresh.customgit.com",
            "build_pipeline": "http://pipeline.com",
        }
        self.assertEqual(payload, expected)

    def test_create_event(self):
        mock = MagicMock()
        client = DataMonitoringClient(mock, mock)
        result = client.create_event("1", "nice", "cool", "http://test.com", "https://fresh.customgit.com")
        self.assertTrue(result)

    def test_create_event_failure(self):
        mock = MagicMock()
        mock.create_event.return_value = False
        client = DataMonitoringClient(mock, mock)
        result = client.create_event("1", "nice", "cool", "http://test.com", "https://fresh.customgit.com")
        self.assertFalse(result)

    @skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
    def test_real_create_event(self):
        client = DataMonitoringClient('NEW_RELIC_API_KEY')
        client.create_event("123", "TESTING", "LOCAL", "http://hi.com", "http://test.net")
