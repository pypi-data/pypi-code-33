import unittest

import mock

from cloudshell.devices.runners.interfaces.firmware_runner_interface import FirmwareRunnerInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(FirmwareRunnerInterface):
            pass
        self.tested_class = TestedClass

    def test_load_firmware(self):
        """Check that instance can't be instantiated without implementation of the "load_firmware" method"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods load_firmware"):
            self.tested_class()

    def test_load_firmware_does_nothing(self):
        class TestedClass(FirmwareRunnerInterface):
            def load_firmware(self, path, vrf_management_name):
                return super(TestedClass, self).load_firmware(path, vrf_management_name)

        tested_class = TestedClass()
        path = mock.MagicMock()
        vrf_management_name = mock.MagicMock()

        self.assertIsNone(tested_class.load_firmware(path, vrf_management_name))
