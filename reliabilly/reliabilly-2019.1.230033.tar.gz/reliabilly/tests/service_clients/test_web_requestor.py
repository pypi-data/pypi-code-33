from unittest import TestCase, skipUnless
from unittest.mock import MagicMock
from reliabilly.components.web.http_requestor import HttpRequestor
from reliabilly.settings import Settings, Constants


GOOGLE_URL = 'http://google.com'


class HttpRequestorTests(TestCase):
    def setUp(self):
        mock = MagicMock()
        mock.get.return_value = mock
        mock.request.return_value = Constants.DUMMY
        self.requestor = HttpRequestor(client=mock)

    def test_get(self):
        result = self.requestor.get(Constants.DUMMY, headers=[])
        self.assertEqual(result, Constants.DUMMY)

    def test_post(self):
        result = self.requestor.post(Constants.DUMMY, data=[], headers=[])
        self.assertEqual(result, Constants.DUMMY)

    def test_put(self):
        result = self.requestor.put(Constants.DUMMY, headers=[])
        self.assertEqual(result, Constants.DUMMY)

    def test_delete(self):
        result = self.requestor.delete(Constants.DUMMY, headers=[])
        self.assertEqual(result, Constants.DUMMY)

    def test_get_items(self):
        mock = MagicMock()
        mock.request.return_value = mock
        mock.json.return_value = {Constants.DUMMY: [1], 'total': 50, 'limit': 1}
        requestor = HttpRequestor(client=mock)
        result = requestor.get_items(Constants.DUMMY, True, Constants.DUMMY)
        self.assertIsNotNone(result)
        result = requestor.get_items(Constants.DUMMY, False, Constants.DUMMY)
        self.assertIsNotNone(result)

    def test_get_all_items(self):
        mock = MagicMock()
        mock.request.return_value = mock
        mock.json.return_value = {Constants.DUMMY: [1], 'total': 50, 'limit': 1}
        requestor = HttpRequestor(client=mock)
        result = requestor.get_all_items(Constants.DUMMY)
        self.assertIsNotNone(result)

    def test_save_items(self):
        mock = MagicMock()
        mock.request.return_value = mock
        mock.json.return_value = {Constants.DUMMY: [1], 'total': 50, 'limit': 1}
        requestor = HttpRequestor(client=mock, save_fn=mock)
        result = requestor.save_data_items(Constants.DUMMY)
        self.assertTrue(result)

    def test_perform_web_request(self):
        mock = MagicMock()
        mock.request.return_value = mock
        mock.json.return_value = {Constants.DUMMY: [1], 'total': 50, 'limit': 1}
        requestor = HttpRequestor(client=mock)
        result = requestor.perform_web_request(Constants.DUMMY, Constants.DUMMY)
        self.assertIsNotNone(result)
        requestor = HttpRequestor(client=mock, circuit_breaker=mock)
        result = requestor.perform_web_request(Constants.DUMMY, Constants.DUMMY)
        self.assertIsNotNone(result)

    def test_get_auth_value(self):
        self.assertIsNotNone(HttpRequestor.get_auth_value(Constants.DUMMY, Constants.DUMMY))

    @skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
    def test_real_get(self):
        requestor = HttpRequestor()
        result = requestor.get(GOOGLE_URL)
        self.assertEqual(result.status_code, Constants.SUCCESS_RESPONSE_CODE)
