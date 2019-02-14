import unittest

import mock

from cloudshell.devices.cli_handler_interface import CliHandlerInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(CliHandlerInterface):
            pass
        self.tested_class = TestedClass

    def test_get_cli_service(self):
        """Check that instance can't be instantiated without implementation of the "get_cli_service" method"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods get_cli_service"):
            self.tested_class()

    def test_get_cli_service_does_nothing(self):
        class TestedClass(CliHandlerInterface):
            def get_cli_service(self, command_mode_type):
                return super(TestedClass, self).get_cli_service(command_mode_type)

        tested_class = TestedClass()

        self.assertIsNone(tested_class.get_cli_service(mock.MagicMock()))
