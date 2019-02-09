""" Handle notifications by email."""
# Standard modules
from email.mime import multipart
from email.mime import text
from email import utils
import gettext
import logging
import smtplib

# Local modules
from vigil import output

gettext.install('vigil', 'locale')
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Email(output.Output):  # pylint: disable=too-few-public-methods
    """
    Represent output via email.

    Attributes:
        subject (str): Subject of notification.
        content (str): Content of notification.
        config (dict): Configuration options.
    """

    def __init__(self, subject, content, config):
        super(Email, self).__init__(subject, content, config)
        self.config = config['email']

    def send(self):
        """
        Send email with given subject and content.

        Args:
            subject(str): Subject of the email.
            content(str): Content of the email.
            config(:obj:`dic`): Config of the SMTP server.
        """
        message = multipart.MIMEMultipart('alternative')
        message['From'] = self.config['from']
        message['To'] = self.config['to']
        message['Subject'] = self.subject
        message['Date'] = utils.formatdate(localtime=True)
        content_type = 'plain'
        message.attach(text.MIMEText(self.content.encode('utf-8'),
                                     content_type, _charset='utf-8'))

        try:
            log.info(_('Connecting to SMTP server server=%s port=%s'),
                     self.config['smtp_host'], self.config['smtp_port'])
            server = smtplib.SMTP_SSL(
                self.config['smtp_host'], self.config['smtp_port'])
        except smtplib.SMTPException as ex:
            log.exception(_('Unable to send email {0}'.format(ex)))
            return False
        except OSError as ex:
            log.error(_('Socket error {0}'.format(ex)))
            return False

        try:
            if self.config['smtp_username'] and self.config['smtp_password']:
                log.info(_('Authenticating...'))
                # Force username and password to string
                server.login(str(self.config['smtp_username']), str(
                    self.config['smtp_password']))

                log.info(_('Sending email to=%s'), message['To'])
                server.sendmail(message['From'], message[
                    'To'], message.as_string())
        except smtplib.SMTPException as ex:
            log.exception(_('Unable to send email {0}'.format(ex)))
            return False
        except IOError as ex:
            log.exception(_('Unable to send email {0}'.format(ex)))
            return False

        log.info(_('Closing connection to server'))
        server.quit()
        return True
