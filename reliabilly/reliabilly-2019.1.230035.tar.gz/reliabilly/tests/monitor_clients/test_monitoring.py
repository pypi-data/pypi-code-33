from unittest import TestCase
from unittest.mock import MagicMock
from reliabilly.components.monitoring import MonitoringProvider, monitor
from reliabilly.settings import Constants


class MonitoringTests(TestCase):
    @staticmethod
    def test_provider():
        mock = MagicMock()
        mock.service_name = Constants.DUMMY
        provider = MonitoringProvider()
        provider.worker_setup(mock)
        provider.worker_result(mock, True)

    def test_decorator(self):
        mock = MagicMock()
        mock.__name__ = Constants.DUMMY
        self.assertTrue(monitor(mock))
        monitor(mock)(mock)

    def test_monitor_ids(self):
        service = 'test'
        method = 'get'
        monitor_prefix = f'{Constants.MONITOR_PREFIX}{service}.{method}'
        monitor_client = MonitoringProvider()
        self.assertEqual(monitor_client.get_monitor_id(service, method, False, False, False),
                         f'{monitor_prefix}{Constants.MONITOR_CALLS_SUFFIX}')
        self.assertEqual(monitor_client.get_monitor_id(service, method, False, True, False),
                         f'{monitor_prefix}{Constants.MONITOR_LARGE_KEY}{Constants.MONITOR_CALLS_SUFFIX}')
        self.assertEqual(monitor_client.get_monitor_id(service, method, False, True, True),
                         f'{monitor_prefix}{Constants.MONITOR_LARGE_KEY}'
                         f'{Constants.MONITOR_ERROR_KEY}{Constants.MONITOR_CALLS_SUFFIX}')
        self.assertEqual(monitor_client.get_monitor_id(service, method, True, False, False),
                         f'{monitor_prefix}{Constants.MONITOR_ELAPSED_SUFFIX}')
        self.assertEqual(monitor_client.get_monitor_id(service, method, True, True, False),
                         f'{monitor_prefix}{Constants.MONITOR_LARGE_KEY}{Constants.MONITOR_ELAPSED_SUFFIX}')
        self.assertEqual(monitor_client.get_monitor_id(service, method, True, True, True),
                         f'{monitor_prefix}{Constants.MONITOR_LARGE_KEY}'
                         f'{Constants.MONITOR_ERROR_KEY}{Constants.MONITOR_ELAPSED_SUFFIX}')

    def test_utility_methods(self):
        mock = MagicMock()
        monitor_client = MonitoringProvider()
        mock.args = "<Request 'http://localhost:8000/test/?f=j&limit=1000' [GET]>"
        result = monitor_client.check_large_page(mock)
        self.assertTrue(result)
        mock.args = "<Request 'http://localhost:8000/test/' [GET]>"
        result = monitor_client.check_large_page(mock)
        self.assertFalse(result)
        mock.args = "<Request 'http://localhost:8000/test/?f=j&limit=10' [GET]>"
        result = monitor_client.check_large_page(mock)
        self.assertFalse(result)
        mock.args = "<Request 'http://localhost:8000/test/?limit=1000' [GET]>"
        result = monitor_client.check_large_page(mock)
        self.assertTrue(result)
        mock.args = ''
        result = monitor_client.check_large_page(mock)
        self.assertFalse(result)
