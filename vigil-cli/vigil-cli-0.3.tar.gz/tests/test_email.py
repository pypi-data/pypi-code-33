# External dependencies
import pytest

# Local modules
from .context import vigil
from vigil.output import email
from . import mailbox


def test_send_email(config, inbox):
    """
    Check that send_email connects to smtp server
    and passes correct parameters.
    """
    email.Email('test', 'test mail', config).send()
    smtp = mailbox.smtp

    assert smtp.address == config['email']['smtp_host']
    assert smtp.port == config['email']['smtp_port']

    assert smtp.username == config['email']['smtp_username']
    assert smtp.password == config['email']['smtp_password']

    assert len(inbox) == 1
    assert inbox[0].from_address == config['email']['from']
    assert inbox[0].to_address == config['email']['to']
