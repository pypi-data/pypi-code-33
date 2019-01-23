import logging
from unittest import TestCase, skipUnless
from unittest.mock import MagicMock

from reliabilly.components.services import ResultTypes
from reliabilly.settings import Settings, Constants
from reliabilly.components.services.sumologic import SumologicQueryExecutor, get_sumologic_api_auth_keys


class SumologicTests(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_execute_sumo_query(self):
        mock, mock_get = MagicMock(), MagicMock()
        mock.status_code = Constants.RECEIVED_SUCCESS_CODE
        mock.json.return_value = {
            "id": "1706867DFC65F3C9",
            "link": {
                "rel": "self",
                "href": "https://api.us2.sumologic.com/api/v1/search/"
                        "jobs/1706867DFC65F3C9"
            }
        }
        mock.post.return_value = mock
        mock_get.status_code = Constants.SUCCESS_RESPONSE_CODE
        mock_get.json.return_value = {Constants.SUMOLOGIC_MESSAGE_COUNT: 5}
        mock.get.return_value = mock_get
        executor = SumologicQueryExecutor(mock)
        self.assertIsNotNone(executor)
        auth_token, app_code = get_sumologic_api_auth_keys(mock, mock, mock)
        result = executor.execute_sumologic_query(
            '_sourceCategory=prod/reliabilly/* error | count',
            '2018-07-06T12:00:00', '2018-07-07T12:00:00',
            auth_token, app_code)
        self.assertEqual(result.value, 5)

    def test_execute_sumo_fail_post(self):
        mock = MagicMock()
        mock.status_code = Constants.BAD_REQUEST_CODE
        mock.post.return_value = mock
        executor = SumologicQueryExecutor(mock)
        self.assertIsNotNone(executor)
        auth_token, app_code = get_sumologic_api_auth_keys(mock, mock, mock)
        result = executor.execute_sumologic_query(
            '_sourceCategory=prod/reliabilly/* error | count',
            '2018-07-06T12:00:00', '2018-07-07T12:00:00',
            auth_token, app_code)
        self.assertIsNone(result.value)

    def test_execute_sumo_fail_error(self):
        mock = MagicMock()
        mock.status_code = Constants.BAD_REQUEST_CODE
        mock.post.side_effect = Exception
        executor = SumologicQueryExecutor(mock)
        self.assertIsNotNone(executor)
        auth_token, app_code = get_sumologic_api_auth_keys(mock, mock, mock)
        result = executor.execute_sumologic_query(
            '_sourceCategory=prod/reliabilly/* error | count',
            '2018-07-06T12:00:00', '2018-07-07T12:00:00',
            auth_token, app_code)
        self.assertIsNone(result.value)

    def test_get_sumo_timer(self):
        mock = MagicMock()
        mock.status_code = Constants.BAD_REQUEST_CODE
        mock.post.side_effect = Exception
        executor = SumologicQueryExecutor(mock)
        self.assertIsNotNone(executor)
        result = executor.get_sumologic_query_results(mock, mock, mock, 1, .1)
        self.assertEqual(ResultTypes.UNKNOWN, result.result)
        self.assertEqual(0, result.value)

    def test_get_sumo_fail(self):
        mock = MagicMock()
        mock.status_code = Constants.BAD_REQUEST_CODE
        mock.get.side_effect = Exception
        executor = SumologicQueryExecutor(mock)
        self.assertIsNotNone(executor)
        result = executor.get_sumologic_query_results(mock, mock, mock)
        self.assertIsNone(result.value)

    @skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
    def test_execute_real(self):
        executor = SumologicQueryExecutor()
        auth_token, app_code = get_sumologic_api_auth_keys('', '')
        result = executor.execute_sumologic_query(
            '_sourceCategory=prod/reliabilly/* error | count',
            '2018-07-06T12:00:00', '2018-07-07T12:00:00',
            auth_token, app_code)
        self.assertTrue(result.value > 0)
