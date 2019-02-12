# __init__.py
__authors__ = ["tsalazar"]
__version__ = "0.1"

import logging
import smtplib
import re
import os.path
from dataclasses import dataclass
from typing import List
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders


@dataclass
class Email:
    """Send an Email with optional attachments.

    Args:
        host: Email server hostname or IP.
        port: Email server port.
        username: Email server account username.
        password: Email server account password.
        sender: Email sender.
        recipients: List of Email recipients.
        subject: Email subject line.
        body: Body of Email.
        use_tls: Connect to the Email server using TLS?
        attachments: Email attachments.
        barracuda_tag: An Email header tag value that forces the Barracuda to encrypt the Email.
    """

    host: str = '127.0.0.1'
    port: str = '25'
    username: str = None
    password: str = None
    sender: str = None
    recipients: List[str] = None
    subject: str = 'No subject'
    body: str = 'No body'
    use_tls: bool = False
    attachments: List[str] = None
    barracuda_tag: str = None

    def __post_init__(self):

        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing Email class object')
        self.__sanity_check()
        self.__send()

    def __sanity_check(self):
        """Are we crazy?"""

        # Email recipients
        assert isinstance(self.recipients, list), self.__logger.critical('email_recipients needs to be a list.')

        if len(self.recipients) > 0:
            for recipient in self.recipients:
                assert re.match(r'[\w.-]+@[\w.-]+', recipient), \
                    self.__logger.critical('Bad Email format found in email_recipients: ' + recipient)
        else:
            self.__logger.critical('No recipients defined!')

        # Hostname
        assert len(self.host) > 0, self.__logger.critical('No hostname defined!')

        # Port
        try:
            if 1 > int(self.port) > 65000:
                self.__logger.critical('Port out of range')
                quit(0)
        except ValueError:
            self.__logger.critical('Port needs to be an integer presented as a string.')
            quit(0)

        # Sender Email
        if re.match(r'[\w.-]+@[\w.-]+', self.sender) is None:
            self.__logger.warning('No valid sender address set.')

        # Subject
        if self.subject is None or self.subject == '':
            self.__logger.warning('subject is empty')

        # Body
        if self.body is None or self.body == '':
            self.__logger.warning('body is empty')

        # Attachment
        if self.attachments is not None:
            for attachment in self.attachments:
                assert os.path.isfile(attachment), self.__logger.critical('Attachment does not exist!')

        self.__logger.debug('Sanity check passed.')
        # self.logger.debug(__dict__)

    def __send(self):
        """Deliver an Email to the mail server."""

        self.__logger.debug('Sending Email.')

        message = MIMEMultipart()
        message['Subject'] = self.subject
        message['From'] = self.sender
        message['To'] = ', '.join(self.recipients)
        if self.barracuda_tag is not None:
            message['X-Barracuda-Encrypted'] = self.barracuda_tag
        # message['X-Barracuda-Encrypted'] = 'ECDHE-RSA-AES256-SHA'
        message.attach(MIMEText(self.body))

        if self.attachments is not None:

            self.__logger.debug('Attachments: ' + str(self.attachments))

            for attachment_item in self.attachments:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(open(attachment_item, 'rb').read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    'attachment; filename="' + os.path.basename(attachment_item) + '"'
                )
                message.attach(attachment)

        # Establish connection to Email server
        email_server = smtplib.SMTP(self.host, self.port)

        # debuglevel 1=messages, 2=timestamped messages
        if self.__logger.level == logging.DEBUG:
            email_server.set_debuglevel(2)

        if self.use_tls is True:
            email_server.starttls()

        if self.username is not None and self.password is not None:
            email_server.login(self.username, self.password)

        # Send Email
        try:
            email_server.send_message(message)

        except ValueError as value_error:
            self.__logger.critical(f'Email send_message error {format(value_error)}')
            exit(1)

        # Close connection to Email server
        email_server.quit()

        self.__logger.debug('Email sent')
