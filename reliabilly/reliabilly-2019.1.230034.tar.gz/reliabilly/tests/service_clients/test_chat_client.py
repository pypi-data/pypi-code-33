from unittest import TestCase
from unittest.mock import MagicMock

from reliabilly.components.chat.chat_client import ChatClient
from reliabilly.settings import Constants

LIVE_TEST_CHANNEL = 'automation-test'
LIVE_TEST_MESSAGE = 'Message generated from unit test run for ChatClient tests.'
LIVE_TEST_EMAIL = 'jared.blouse@reliabilly.com'


class ChatClientTests(TestCase):
    def test_send_room_message(self):
        mock = MagicMock()
        chat_client = ChatClient(mock)
        self.assertTrue(chat_client.send_room_message(Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.send_message.called)

    def test_send_user_message(self):
        mock = MagicMock()
        chat_client = ChatClient(mock)
        self.assertTrue(chat_client.send_user_message(Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.send_dm.called)

    def test_update_message(self):
        mock = MagicMock()
        chat_client = ChatClient(mock)
        self.assertTrue(chat_client.update_message(Constants.DUMMY, Constants.DUMMY, Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.update_message.called)

    def test_send_ephemeral_message(self):
        mock = MagicMock()
        chat_client = ChatClient(mock)
        self.assertTrue(chat_client.send_ephemeral_message(Constants.DUMMY, Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.send_ephemeral_message.called)

    def test_add_reaction(self):
        mock = MagicMock()
        chat_client = ChatClient(mock)
        self.assertTrue(chat_client.add_reaction(Constants.DUMMY, Constants.DUMMY, Constants.DUMMY))
        self.assertTrue(mock.add_reaction.called)
