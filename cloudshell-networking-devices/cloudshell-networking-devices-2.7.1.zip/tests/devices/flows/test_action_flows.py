import unittest

import mock

from cloudshell.devices.flows.action_flows import RunCommandFlow, SaveConfigurationFlow, \
    RestoreConfigurationFlow, AddVlanFlow, RemoveVlanFlow, LoadFirmwareFlow


class TestRunCommandFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.run_flow = RunCommandFlow(cli_handler=self.cli_handler,
                                       logger=self.logger)

    def test_execute_flow_in_enable_mode(self):
        """Check that method will get CLI session in the enable mode and return response from the device"""
        custom_command = "test command"
        response = "test response"
        session = mock.MagicMock(send_command=mock.MagicMock(return_value=response))
        self.cli_handler.get_cli_service.return_value = mock.MagicMock(__enter__=mock.MagicMock(return_value=session))
        # act
        result = self.run_flow.execute_flow(custom_command=custom_command)
        # verify
        self.assertEqual(result, response)
        self.cli_handler.get_cli_service.assert_called_once_with(self.cli_handler.enable_mode)

    def test_execute_flow_in_config_mode(self):
        """Check that method will get CLI session in the config mode and return response from the device"""
        custom_command = "test command"
        response = "test response"
        session = mock.MagicMock(send_command=mock.MagicMock(return_value=response))
        self.cli_handler.get_cli_service.return_value = mock.MagicMock(__enter__=mock.MagicMock(return_value=session))
        # act
        result = self.run_flow.execute_flow(custom_command=custom_command,
                                            is_config=True)
        # verify
        self.assertEqual(result, response)
        self.cli_handler.get_cli_service.assert_called_once_with(self.cli_handler.config_mode)

    def test_execute_flow_enable_mode_is_none(self):
        """Check that method will raise exception if enable_mode is None"""
        custom_command = "test command"
        self.cli_handler.enable_mode = None
        # act
        with self.assertRaisesRegexp(Exception, "Enable Mode has to be defined"):
            self.run_flow.execute_flow(custom_command=custom_command)

    def test_execute_flow_config_mode_is_none(self):
        """Check that method will raise exception if config_mode is None"""
        custom_command = "test command"
        self.cli_handler.config_mode = None
        # act
        with self.assertRaisesRegexp(Exception, "Config Mode has to be defined"):
            self.run_flow.execute_flow(custom_command=custom_command, is_config=True)

    def test_execute_flow_commands_in_tuple(self):
        custom_commands = ('test command 1', 'test command 2')
        responses = ('test response 1', 'test response 2')

        session = mock.MagicMock(send_command=mock.MagicMock(side_effect=responses))
        self.cli_handler.get_cli_service.return_value = mock.MagicMock(
            __enter__=mock.MagicMock(return_value=session))

        result = self.run_flow.execute_flow(custom_commands)

        self.assertEqual('\n'.join(responses), result)

    def test_execute_flow_commands_in_list(self):
        custom_commands = ['test command 1', 'test command 2']
        responses = ('test response 1', 'test response 2')

        session = mock.MagicMock(send_command=mock.MagicMock(side_effect=responses))
        self.cli_handler.get_cli_service.return_value = mock.MagicMock(
            __enter__=mock.MagicMock(return_value=session))

        result = self.run_flow.execute_flow(custom_commands)

        self.assertEqual('\n'.join(responses), result)


class TestSaveConfigurationFlow(unittest.TestCase):
    def test_execute_flow_does_nothing(self):
        class TestedClass(SaveConfigurationFlow):
            def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
                return super(TestedClass, self).execute_flow(
                    folder_path, configuration_type, vrf_management_name)

        cli_handler = mock.MagicMock()
        logger = mock.MagicMock()
        tested_class = TestedClass(cli_handler, logger)

        folder_path = mock.MagicMock()
        configuration_type = mock.MagicMock()

        self.assertIsNone(tested_class.execute_flow(folder_path, configuration_type))


class TestRestoreConfigurationFlow(unittest.TestCase):
    def test_execute_flow_does_nothing(self):
        class TestedClass(RestoreConfigurationFlow):
            def execute_flow(self, path, restore_method, configuration_type, vrf_management_name):
                return super(TestedClass, self).execute_flow(
                    path, restore_method, configuration_type, vrf_management_name)

        cli_handler = mock.MagicMock()
        logger = mock.MagicMock()
        tested_class = TestedClass(cli_handler, logger)

        path = mock.MagicMock()
        restore_method = mock.MagicMock()
        configuration_type = mock.MagicMock()
        vrf_management_name = mock.MagicMock()

        self.assertIsNone(tested_class.execute_flow(
            path, restore_method, configuration_type, vrf_management_name))


class TestAddVlanFlow(unittest.TestCase):
    def test_execute_flow_does_nothing(self):
        class TestedClass(AddVlanFlow):
            def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
                return super(TestedClass, self).execute_flow(
                    vlan_range, port_mode, port_name, qnq, c_tag)

        cli_handler = mock.MagicMock()
        logger = mock.MagicMock()
        tested_class = TestedClass(cli_handler, logger)

        vlan_range = mock.MagicMock()
        port_mode = mock.MagicMock()
        port_name = mock.MagicMock()
        qnq = mock.MagicMock()
        c_tag = mock.MagicMock()

        self.assertIsNone(tested_class.execute_flow(vlan_range, port_mode, port_name, qnq, c_tag))


class TestRemoveVlanFlow(unittest.TestCase):
    def test_execute_flow_does_nothing(self):
        class TestedClass(RemoveVlanFlow):
            def execute_flow(self, vlan_range, port_name, port_mode, action_map=None,
                             error_map=None):
                return super(TestedClass, self).execute_flow(
                    vlan_range, port_name, port_mode, action_map, error_map)

        cli_handler = mock.MagicMock()
        logger = mock.MagicMock()
        tested_class = TestedClass(cli_handler, logger)

        vlan_range = mock.MagicMock()
        port_name = mock.MagicMock()
        port_mode = mock.MagicMock()
        action_map = mock.MagicMock()
        error_map = mock.MagicMock()

        self.assertIsNone(tested_class.execute_flow(
            vlan_range, port_name, port_mode, action_map, error_map))


class TestLoadFirmwareFlow(unittest.TestCase):
    def test_execute_flow_does_nothing(self):
        class TestedClass(LoadFirmwareFlow):
            def execute_flow(self, path, vrf, timeout):
                return super(TestedClass, self).execute_flow(path, vrf, timeout)

        cli_handler = mock.MagicMock()
        logger = mock.MagicMock()
        tested_class = TestedClass(cli_handler, logger)

        path = mock.MagicMock()
        vrf = mock.MagicMock()
        timeout = mock.MagicMock()

        self.assertIsNone(tested_class.execute_flow(path, vrf, timeout))
