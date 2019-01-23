from reliabilly.tests import MagicMock, TestCase, logging, warnings, json, skipUnless
from reliabilly.components.tools.stats_client import StatsLogClient, monitor_collection_status, StatsWebClient
from reliabilly.settings import Constants, Settings
from reliabilly.components.web.http_requestor import HttpRequestor


class StatsLogClientTests(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        warnings.filterwarnings(Constants.IGNORE, category=ResourceWarning)

    def test_add_timing(self):
        mock = MagicMock()
        stats_client = StatsLogClient(client=mock, secrets_manager=mock, http_client=mock)
        stats_client.add_timing(Constants.DUMMY, Constants.DUMMY_NUM)
        mock.timing.assert_called_once_with(Constants.DUMMY, Constants.DUMMY_NUM)
        mock.timing.side_effect = Exception
        self.assertFalse(stats_client.add_timing(Constants.DUMMY, Constants.DUMMY_NUM))

    def test_update_increment_with_tags(self):
        mock = MagicMock()
        mock.incr.return_value = True
        stats_client = StatsLogClient(client=mock, secrets_manager=mock, http_client=mock)
        name = 'collection_failure'
        value = 1
        tags = {'env': 'local'}
        result = stats_client.update_increment(name, value, tags)
        mock.incr.assert_called_once_with(name, value, tags=tags)
        self.assertTrue(result)

    def test_update_increment_no_tags(self):
        mock = MagicMock()
        mock.incr.return_value = True
        stats_client = StatsLogClient(client=mock, secrets_manager=mock, http_client=mock)
        name = 'collection_failure'
        value = 1
        result = stats_client.update_increment(name, value)
        mock.incr.assert_called_once_with(name, value)
        self.assertTrue(result)

    def test_update_increment(self):
        mock = MagicMock()
        mock.incr.side_effect = Exception
        stats_client = StatsLogClient(client=mock, secrets_manager=mock, http_client=mock)
        name = 'collection_failure'
        value = 1
        self.assertFalse(stats_client.update_increment(name, value))

    def test_add_gauge_defaults(self):
        mock = MagicMock()
        stats_client = StatsLogClient(client=mock, secrets_manager=mock, http_client=mock)
        name = 'test_stat'
        value = 0
        tags = {'tag1': 'tag1_value', 'tag2': 'tag2_value'}
        result = stats_client.add_gauge(name, value, tags)
        mock.gauge.assert_called_once_with(name, value, delta=False, rate=1, tags=tags)
        self.assertTrue(result)

    def test_add_gauge_no_tags(self):
        mock = MagicMock()
        stats_client = StatsLogClient(client=mock, secrets_manager=mock, http_client=mock)
        name = 'test_stat'
        value = 0
        result = stats_client.add_gauge(name, value)
        mock.gauge.assert_called_once_with(name, value, delta=False, rate=1)
        self.assertTrue(result)

    def test_add_gauge_exception(self):
        mock = MagicMock()
        mock.gauge.side_effect = Exception('test')
        stats_client = StatsLogClient(client=mock, secrets_manager=mock, http_client=mock)
        name = 'test_stat'
        value = 0
        tags = {'tag1': 'tag1_value', 'tag2': 'tag2_value'}
        result = stats_client.add_gauge(name, value, tags)
        self.assertFalse(result)

    def test_add_incr(self):
        @monitor_collection_status('local')
        def test_func_true():
            return True
        result = test_func_true()
        self.assertTrue(result)

        @monitor_collection_status('local')
        def test_func_false():
            return False
        result = test_func_false()
        self.assertFalse(result)


class StatsWebClientTests(TestCase):
    def test_web_payload(self):
        payload = StatsWebClient.get_web_metrics_payload(
            Constants.DUMMY, 55.55, {Constants.PRODUCT: Constants.DUMMY, Constants.DUMMY: Constants.DUMMY_NUM})
        self.assertIsNotNone(payload)
        payload_dictionary = json.loads(payload)
        self.assertEqual(payload_dictionary[Constants.METRIC_NAME_KEY], Constants.DUMMY)
        self.assertEqual(payload_dictionary[Constants.METRIC_VALUE_KEY], 55.55)
        self.assertEqual(payload_dictionary[Constants.METRIC_TAG_KEY_PREFIX + Constants.PRODUCT], Constants.DUMMY)
        self.assertEqual(payload_dictionary[Constants.METRIC_TAG_KEY_PREFIX + Constants.DUMMY], Constants.DUMMY_NUM)

    def test_get_web_api_key(self):
        mock = MagicMock()
        stats_client = StatsWebClient(secrets_manager=mock, http_client=mock)
        self.assertIsNotNone(stats_client.get_api_key())
        self.assertEqual(stats_client.get_api_key(Constants.DUMMY), Constants.DUMMY)

    def test_gauge(self):
        mock = MagicMock()
        stats_client = StatsWebClient(secrets_manager=mock, http_client=mock)
        self.assertTrue(stats_client.add_gauge(Constants.DUMMY, Constants.DUMMY_NUM, {}))
        mock.get_secret.side_effect = Exception
        self.assertFalse(stats_client.add_gauge(Constants.DUMMY, Constants.DUMMY_NUM, {}))

    def test_timing(self):
        mock = MagicMock()
        stats_client = StatsWebClient(secrets_manager=mock, http_client=mock)
        self.assertTrue(stats_client.add_timing(Constants.DUMMY, Constants.DUMMY_NUM, {}))
        mock.get_secret.side_effect = Exception
        self.assertFalse(stats_client.add_timing(Constants.DUMMY, Constants.DUMMY_NUM, {}))

    def test_increment(self):
        mock = MagicMock()
        stats_client = StatsWebClient(secrets_manager=mock, http_client=mock)
        self.assertTrue(stats_client.update_increment(Constants.DUMMY, Constants.DUMMY_NUM, {}))
        mock.get_secret.side_effect = Exception
        self.assertFalse(stats_client.update_increment(Constants.DUMMY, Constants.DUMMY_NUM, {}))

    @skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
    def test_real_web_send(self):
        mock = MagicMock()
        mock.get_secret.return_value = ''
        stats_client = StatsWebClient(secrets_manager=mock, http_client=HttpRequestor())
        self.assertTrue(stats_client.add_gauge('odb', 20, {Constants.PRODUCT: 'odb'}))
