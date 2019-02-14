import unittest

import mock

from cloudshell.devices.runners.run_command_runner import RunCommandRunner


class TestRunCommandRunner(unittest.TestCase):
    def setUp(self):
        self.tested_class = RunCommandRunner
        self.logger = mock.MagicMock()
        self.cli_handler = mock.MagicMock()
        self.runner = RunCommandRunner(logger=self.logger, cli_handler=self.cli_handler)

    @mock.patch("cloudshell.devices.runners.run_command_runner.RunCommandFlow")
    def test_run_custom_command(self, run_command_flow_class):
        """Check that method will execute RunCommandFlow flow without is_config flag"""
        custom_command = "test custom command"
        expected_res = mock.MagicMock()
        run_command_flow = mock.MagicMock(
            execute_flow=mock.MagicMock(
                return_value=expected_res))

        run_command_flow_class.return_value = run_command_flow
        # act
        with mock.patch.object(self.tested_class, "cli_handler") as cli_handler:
            result = self.runner.run_custom_command(custom_command=custom_command)

            # verify
            self.assertEqual(result, expected_res)
            run_command_flow_class.assert_called_once_with(cli_handler, self.logger)
            run_command_flow.execute_flow.assert_called_once_with(custom_command=custom_command)

    @mock.patch("cloudshell.devices.runners.run_command_runner.RunCommandFlow")
    def test_run_custom_config_command(self, run_command_flow_class):
        """Check that method will execute RunCommandFlow flow with is_config flag"""
        custom_command = "test custom command"
        expected_res = mock.MagicMock()
        run_command_flow = mock.MagicMock(
            execute_flow=mock.MagicMock(
                return_value=expected_res))

        run_command_flow_class.return_value = run_command_flow
        # act
        with mock.patch.object(self.tested_class, "cli_handler") as cli_handler:
            result = self.runner.run_custom_config_command(custom_command=custom_command)

            # verify
            self.assertEqual(result, expected_res)
            run_command_flow_class.assert_called_once_with(cli_handler, self.logger)
            run_command_flow.execute_flow.assert_called_once_with(custom_command=custom_command,
                                                                  is_config=True)

    def test_prop_cli_handler(self):
        self.assertEqual(self.cli_handler, self.runner.cli_handler)
