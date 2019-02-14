from unittest import TestCase

from mock import Mock, patch, PropertyMock

from cloudshell.tg.breaking_point.runners.bp_runner import BPRunner


class BPRunnerImpl(BPRunner):
    pass


class TestBPRunner(TestCase):
    def setUp(self):
        self._api = Mock()
        self._logger = Mock()
        self._instance = BPRunnerImpl(self._api, self._logger)

    def test_api_property(self):
        self.assertIs(self._instance.api, self._api)

    def test_logger_property(self):
        self.assertIs(self._instance.logger, self._logger)
