import unittest

import mock

from cloudshell.devices.standards.traffic.chassis.configuration_attributes_structure import \
    GenericTrafficChassisResource


class TestGenericTrafficChassisResource(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.supported_os = ["test OS"]
        self.resource = GenericTrafficChassisResource(shell_name=self.shell_name,
                                                      name=self.name,
                                                      supported_os=self.supported_os)

    def test_user(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "User"): expected_val
        }
        # act
        result = self.resource.user
        # verify
        self.assertEqual(result, expected_val)

    def test_password(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Password"): expected_val
        }
        # act
        result = self.resource.password
        # verify
        self.assertEqual(result, expected_val)

    def test_controller_tcp_port(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Controller TCP Port"): expected_val
        }
        # act
        result = self.resource.controller_tcp_port
        # verify
        self.assertEqual(result, expected_val)

    def test_controller_address(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Controller Address"): expected_val
        }
        # act
        result = self.resource.controller_address
        # verify
        self.assertEqual(result, expected_val)

    def test_client_install_path(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Client Install Path"): expected_val
        }
        # act
        result = self.resource.client_install_path
        # verify
        self.assertEqual(result, expected_val)

    def test_power_management(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Power Management"): expected_val
        }
        # act
        result = self.resource.power_management
        # verify
        self.assertEqual(result, expected_val)

    def test_from_context(self):
        """Check that method will create and return GenericNetworkingResource instance from given context"""
        shell_name = "test shell name"
        supported_os = ["test OS"]
        context = mock.MagicMock()
        # act
        result = GenericTrafficChassisResource.from_context(shell_name=shell_name,
                                                            supported_os=supported_os,
                                                            context=context)
        # verify
        self.assertIsInstance(result, GenericTrafficChassisResource)
