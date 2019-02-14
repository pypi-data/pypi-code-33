import unittest

import mock

from cloudshell.devices.runners.interfaces.run_command_runner_interface import RunCommandInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(RunCommandInterface):
            pass
        self.tested_class = TestedClass

    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of all abstract methods"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods run_custom_command, run_custom_config_command"):
            self.tested_class()

    def test_abstract_methods_do_nothing(self):
        class TestedClass(RunCommandInterface):
            def run_custom_command(self, command):
                return super(TestedClass, self).run_custom_command(command)

            def run_custom_config_command(self, command):
                return super(TestedClass, self).run_custom_config_command(command)

        tested_class = TestedClass()
        command = mock.MagicMock()

        self.assertIsNone(tested_class.run_custom_command(command))
        self.assertIsNone(tested_class.run_custom_config_command(command))
