from unittest import TestCase

from mock import Mock

from cloudshell.tg.breaking_point.rest_actions.rest_actions import RestActions


class TestRestActions(TestCase):
    def setUp(self):
        self._rest_service = Mock()
        self._logger = Mock()
        self._instance = RestActions(self._rest_service, self._logger)

    def test_init(self):
        self.assertIs(self._rest_service, self._instance._rest_service)
        self.assertIs(self._logger, self._instance._logger)
