# pylint: disable=missing-docstring

import unittest
from mock import patch, Mock
from opentmi_client.cli.main import opentmiclient_main, OpentTMIClientCLI


FAKE_TOKEN = "a.b.c"


class TestCli(unittest.TestCase):
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_help(self, mock_exit, mock_stdout):
        fake_args = ["opentmi", "--help"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_version(self, mock_exit, mock_stdout):
        fake_args = ["opentmi", "version"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_version_verbose(self, mock_exit, mock_stdout):
        fake_args = ["opentmi", "-v", "version"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_verbose_levels(self, mock_exit, mock_stdout):

        fake_args = ["opentmi", "-v", "version"]
        with patch('sys.argv', fake_args):
            cli = OpentTMIClientCLI()

        fake_args = ["opentmi", "-vv", "version"]
        with patch('sys.argv', fake_args):
            cli = OpentTMIClientCLI()

        fake_args = ["opentmi", "-vvv", "version"]
        with patch('sys.argv', fake_args):
            cli = OpentTMIClientCLI()

        fake_args = ["opentmi", "-vvvv", "version"]
        with patch('sys.argv', fake_args):
            cli = OpentTMIClientCLI()

    @patch('opentmi_client.transport.Transport.get_json', returns=[{"tcid": "b", "name": "c"}])
    @patch('opentmi_client.transport.Transport.post_json', returns={"token": "a.b.c"})
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_list_testcases(self, mock_exit, _mock_stdout, mock_list, mock_token):
        fake_args = ["opentmi", "--token", FAKE_TOKEN, "list", "--testcases"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('opentmi_client.transport.Transport.get_json', returns=[{"tcid": "b", "name": "c"}])
    @patch('opentmi_client.transport.Transport.post_json', returns={"token": "a.b.c"})
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_list_campaigns(self, mock_exit, _mock_stdout, mock_token, mock_list):
        fake_args = ["opentmi", "--token", FAKE_TOKEN, "list", "--campaigns"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('opentmi_client.transport.Transport.get_json', returns=[{"tcid": "b", "name": "c"}])
    @patch('opentmi_client.transport.Transport.post_json', returns={"token": "a.b.c"})
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_list_results_json(self, mock_exit, _mock_stdout, mock_token, mock_list):
        fake_args = ["opentmi", "--token", FAKE_TOKEN, "list", "--testcases", "--json"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('opentmi_client.transport.Transport.get_json', returns=[{"tcid": "b", "name": "c"}])
    @patch('opentmi_client.transport.Transport.post_json', returns={"token": "a.b.c"})
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_list_results_json(self, mock_exit, _mock_stdout, mock_token, mock_list):
        fake_args = ["opentmi", "--token", FAKE_TOKEN, "list", "--campaigns", "--json"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)
