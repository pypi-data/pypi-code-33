import json
import logging
import os
from unittest import TestCase, skipUnless
from unittest.mock import MagicMock
from reliabilly.settings import Settings, Constants
from reliabilly.components.services.newrelic import NewRelicQueryExecutor, ResultTypes


# noinspection SqlDialectInspection
class NewRelicTests(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_execute_newrelic_query(self):
        mock_new_relic_query = MagicMock()
        mock = MagicMock()
        mock.get_secret.return_value = Constants.EMPTY
        new_relic_query_response = self.get_test_data(
            'test_files/new_relic_query_response.json')
        mock_new_relic_query.get.return_value = mock_new_relic_query
        mock_new_relic_query.json.return_value = new_relic_query_response
        runner = NewRelicQueryExecutor(mock, mock_new_relic_query, mock)
        results = runner.execute_single_value_query(mock_new_relic_query)
        self.assertEqual(0.42081991001201285, results.value)

    def test_execute_facet_query(self):
        mock_new_relic_query = MagicMock()
        mock = MagicMock()
        mock.get_secret.return_value = Constants.EMPTY
        new_relic_query_response = self.get_test_data(
            'test_files/new_relic_facet_query_response.json')
        mock_new_relic_query.get.return_value = mock_new_relic_query
        mock_new_relic_query.json.return_value = new_relic_query_response
        runner = NewRelicQueryExecutor(mock, mock_new_relic_query, mock)
        results = runner.execute_faceted_query(mock_new_relic_query)
        self.assertEqual(
            100, results.value[Constants.FACETS][0][Constants.RESULTS][0][Constants.RESULT])
        mock_new_relic_query.ok = False
        results = runner.execute_faceted_query(mock_new_relic_query)
        self.assertEqual(ResultTypes.ERROR, results.result)

    def test_execute_query_failure(self):
        mock_new_relic_query = MagicMock()
        mock = MagicMock()
        new_relic_query_response = self.get_test_data(
            'test_files/new_relic_query_empty_response.json')
        mock_new_relic_query.get.return_value = mock_new_relic_query
        mock_new_relic_query.json.return_value = new_relic_query_response
        runner = NewRelicQueryExecutor(mock, mock_new_relic_query, mock)
        results = runner.execute_single_value_query(mock_new_relic_query)
        self.assertEqual(ResultTypes.UNKNOWN, results.result)

    def test_execute_results_missing(self):
        mock_new_relic_query = MagicMock()
        mock = MagicMock()
        new_relic_query_response = self.get_test_data(
            'test_files/new_relic_query_missing_results.json')
        mock_new_relic_query.json.return_value = new_relic_query_response
        mock_new_relic_query.get.return_value = mock_new_relic_query
        runner = NewRelicQueryExecutor(mock, mock_new_relic_query, mock)
        results = runner.execute_single_value_query(mock_new_relic_query)
        self.assertEqual(ResultTypes.UNKNOWN, results.result)

    def test_execute_results_null(self):
        mock_new_relic_query = MagicMock()
        mock = MagicMock()
        new_relic_query_response = self.get_test_data(
            'test_files/new_relic_query_null_response.json')
        mock_new_relic_query.get.return_value = mock_new_relic_query
        mock_new_relic_query.json.return_value = new_relic_query_response
        runner = NewRelicQueryExecutor(mock, mock_new_relic_query, mock)
        results = runner.execute_single_value_query(mock_new_relic_query)
        self.assertEqual(ResultTypes.SUCCESS, results.result)
        self.assertEqual(None, results.value)

    @skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
    def test_execute_live(self):
        runner = NewRelicQueryExecutor(Constants.EMPTY)
        results = runner.execute_single_value_query(Constants.EMPTY)
        self.assertEqual(141.71249771118164, results)

    def test_url_build(self):
        account_id = 12345678
        query = "SELECT average(`get_elapsed.median`) as ms " \
                "FROM reliabilly_statsd WHERE app LIKE 'infrastructure'" \
                "since 1 month ago"
        results = NewRelicQueryExecutor(
            Constants.EMPTY).build_url(account_id, query)
        self.assertEqual("https://insights-api.newrelic.com/v1/accounts/"
                         "12345678/query?nrql=SELECT%20average%28%60"
                         "get_elapsed.median%60%29%20as%20ms%20FROM%20"
                         "reliabilly_statsd%20WHERE%20app%20LIKE%20%27"
                         "infrastructure%27since%201%20month%20ago", results)

    @staticmethod
    def get_test_data(file):
        test_path = os.path.join(
            os.path.dirname(__file__), file)
        with open(test_path) as test_file:
            return json.load(test_file)
