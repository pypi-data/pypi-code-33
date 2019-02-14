from unittest import TestCase

from mock import Mock

from cloudshell.tg.breaking_point.flows.bp_flow import BPFlow


class TestBPFlow(TestCase):
    def setUp(self):
        self._session_context_manager = Mock()
        self._logger = Mock()
        self._instance = BPFlow(self._session_context_manager, self._logger)

    def test_init(self):
        self.assertIs(self._instance._session_context_manager, self._session_context_manager)
        self.assertIs(self._instance._logger, self._logger)
