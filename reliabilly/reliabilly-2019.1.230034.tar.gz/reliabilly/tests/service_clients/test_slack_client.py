import unittest
from unittest.mock import MagicMock

from reliabilly.components.chat.slack_client import SlackClient
from reliabilly.settings import Constants

MOCK_RETURN = {'ok': True, 'channel': 'C9Q0CTJBV',
               'ts': '1521062111.000062', 'message':
                   {'text': 'Test',
                    'username': 'Test',
                    'bot_id': 'B5CGL790F', 'type': 'message',
                    'subtype': 'bot_message', 'ts': '1521062111.000062'}}
MOCK_USERS = {'users': [{'slack': {'id': 'hello'}}], 'total': 1}


class SlackClientTests(unittest.TestCase):
    def test_send_message(self):
        mock = MagicMock()
        mock.api_call.return_value = MOCK_RETURN
        slack_client = SlackClient(mock, mock)
        self.assertTrue(slack_client.send_message(Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.api_call.called)

    def test_send_dm(self):
        mock = MagicMock()
        request_mock = MagicMock()
        request_mock.json.return_value = MOCK_USERS
        mock.get.return_value = request_mock
        mock.api_call.return_value = MOCK_RETURN
        slack_client = SlackClient(mock, mock)
        self.assertTrue(slack_client.send_dm(Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.api_call.called)

    def test_update_message(self):
        mock = MagicMock()
        mock.api_call.return_value = MOCK_RETURN
        slack_client = SlackClient(mock, mock)
        self.assertTrue(slack_client.update_message(Constants.DUMMY, Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.api_call.called)

    def test_send_ephemeral_message(self):
        mock = MagicMock()
        mock.api_call.return_value = MOCK_RETURN
        slack_client = SlackClient(mock, mock)
        self.assertTrue(slack_client.send_ephemeral_message(Constants.DUMMY, Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.api_call.called)

    def test_add_reaction(self):
        mock = MagicMock()
        mock.api_call.return_value = MOCK_RETURN
        slack_client = SlackClient(mock, mock)
        self.assertTrue(slack_client.add_reaction(Constants.DUMMY, Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.api_call.called)
