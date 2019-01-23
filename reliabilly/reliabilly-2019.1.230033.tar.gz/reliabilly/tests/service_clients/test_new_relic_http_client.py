import unittest
from unittest.mock import MagicMock

from reliabilly.components.tools.newrelic_http_client import NewRelicHttpClient


class NewRelicHttpClientTests(unittest.TestCase):

    def test_generate_headers(self):
        client = NewRelicHttpClient("sand-rabbits", "http://nice.com")
        actual = client.generate_headers()
        expected = {'Content-Type': 'application/json', 'X-Insert-Key': 'sand-rabbits'}
        self.assertEqual(expected, actual)

    def test_create_event(self):
        mock = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock.post.return_value = mock_response
        payload = {'eventType': 'release', 'title': 'Does not really matter'}
        client = NewRelicHttpClient('huh', 'http://neat.com')
        actual = client.create_event(payload, mock)
        self.assertTrue(actual)

    def test_create_event_failure(self):
        mock = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock.post.return_value = mock_response
        payload = {'eventType': 'release', 'title': 'Does not really matter'}
        client = NewRelicHttpClient('huh', 'http://neat.com')
        actual = client.create_event(payload, mock)
        self.assertFalse(actual)
