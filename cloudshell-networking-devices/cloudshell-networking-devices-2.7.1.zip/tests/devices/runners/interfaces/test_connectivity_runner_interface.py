import unittest

import mock

from cloudshell.devices.runners.interfaces.connectivity_runner_interface import ConnectivityOperationsInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(ConnectivityOperationsInterface):
            pass
        self.tested_class = TestedClass

    def test_apply_connectivity_changes(self):
        """Check that instance can't be instantiated without implementation of the 'apply_connectivity_changes'"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods apply_connectivity_changes"):
            self.tested_class()

    def test_apply_connectivity_changes_does_nothing(self):
        class TestedClass(ConnectivityOperationsInterface):
            def apply_connectivity_changes(self, request):
                return super(TestedClass, self).apply_connectivity_changes(request)

        tested_class = TestedClass()
        request = mock.MagicMock()

        self.assertIsNone(tested_class.apply_connectivity_changes(request))
