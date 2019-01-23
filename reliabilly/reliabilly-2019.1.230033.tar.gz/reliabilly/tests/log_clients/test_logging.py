from unittest import TestCase
from unittest.mock import MagicMock
from reliabilly.components.logger import LoggingProvider, SumoLogClient, PingLogFilter
from reliabilly.settings import Constants


class LoggingTests(TestCase):
    @staticmethod
    def test_log_debug():
        mock = MagicMock()
        logger = LoggingProvider(Constants.DUMMY, mock, mock)
        logger.debug(Constants.DUMMY)
        mock.debug.assert_called_once()

    @staticmethod
    def test_log_error():
        mock = MagicMock()
        logger = LoggingProvider(Constants.DUMMY, mock, mock)
        logger.error(Constants.DUMMY)
        mock.error.assert_called_once()

    @staticmethod
    def test_log_info():
        mock = MagicMock()
        logger = LoggingProvider(Constants.DUMMY, mock, mock)
        logger.info(Constants.DUMMY)
        mock.info.assert_called_once()

    @staticmethod
    def test_log_critical():
        mock = MagicMock()
        logger = LoggingProvider(Constants.DUMMY, mock, mock)
        logger.critical(Constants.DUMMY)
        mock.critical.assert_called_once()

    def test_get_dependency(self):
        mock = MagicMock()
        logger = LoggingProvider(Constants.DUMMY, mock, mock)
        self.assertEqual(logger.get_dependency(Constants.DUMMY), mock)

    def test_worker_setup(self):
        mock = MagicMock()
        mock.service_name = Constants.DUMMY
        logger = LoggingProvider(Constants.DUMMY, mock, mock)
        logger.worker_setup(mock)
        self.assertEqual(logger.log_name, Constants.DUMMY)

    def test_logger(self):
        logger = LoggingProvider(Constants.DUMMY)
        self.assertIsNotNone(logger)

    def test_ping_filter(self):
        mock = MagicMock()
        mock.getMessage.return_value = 'ping test'
        filter_client = PingLogFilter()
        self.assertFalse(filter_client.filter(mock))
        mock.getMessage.return_value = 'test not'
        self.assertTrue(filter_client.filter(mock))

    def test_sumo_logger(self):
        mock = MagicMock()
        mock.status_code = 200
        mock.post.return_value = mock
        logger = SumoLogClient(mock, 'dummy')
        self.assertEqual(logger.get_environment(), Constants.UAT)
        self.assertEqual(logger.get_environment(Constants.PROD_REGION),
                         Constants.PROD)
        headers = logger.get_headers('jjb-ut')
        self.assertIsNotNone(headers)
        self.assertTrue(logger.ship_log('debug', 'jjb-ut', 'test message'))
        mock.status_code = 404
        self.assertFalse(logger.ship_log('debug', 'jjb-ut', 'test message'))
        mock.post.side_effect = Exception
        self.assertFalse(logger.ship_log('debug', 'jjb-ut', 'test message'))
