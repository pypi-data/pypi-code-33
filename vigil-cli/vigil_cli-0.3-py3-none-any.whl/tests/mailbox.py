# Standard modules
import base64
import smtplib

# External dependencies
import pytest

# Local modules
from .context import vigil

# Inbox for storing mock messages
mailbox = []


class Message:
    """
    Mock Message sent to SMTP server.
    """

    def __init__(self, from_address, to_address, fullmessage):
        self.from_address = from_address
        self.to_address = to_address
        self.fullmessage = fullmessage

    def get_message(self):
        """
        Get decoded content part of the message.
        """
        # Get the body of the message
        message = ''.join(self.fullmessage.splitlines()[12:-2])
        return self._from_b64(message)

    @staticmethod
    def _from_b64(string):
        return base64.b64decode(string.encode('utf-8')).decode()


class DummySMTP:
    """
    Mock SMTP server for testing purposes.
    """

    def __init__(self, address, port):
        self.address = address
        self.port = port
        global smtp
        smtp = self

    def login(self, username, password):
        """
        Save login credentials.
        """
        self.username = username
        self.password = password
        global smtp

    def sendmail(self, from_address, to_address, fullmessage):
        """
        Send mock message to inbox.
        """
        global mailbox
        mailbox.append(Message(from_address, to_address, fullmessage))
        return []

    def quit(self):
        self.has_quit = True


@pytest.fixture
def inbox(monkeypatch):
    # Monkeypatch smtplib.SMTP_SSL
    monkeypatch.setattr(smtplib, 'SMTP_SSL', DummySMTP)

    global mailbox
    yield mailbox
    mailbox = []
