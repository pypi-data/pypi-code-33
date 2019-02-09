import os
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def _you_shall_not_pass(func):
    """
    Decorator for the methods when it is need to check the status of an email.
    """
    def wrapper(email, *args, **kwargs):
        if email.used is True:
            func(email, *args, **kwargs)
    return wrapper

class Email():
    """
    That class represents SMTP server and email used to send notifications
    and alarms generated in the log.
    """
    def __init__ (
        self, log, address=None, ip=None, port=None, user=None,
        password=None, tls=True, recipients=None
    ):
        used = True if address is not None and address is not False else False
        self.used = used
        self.log = log
        self.address = address

        self.ip = ip
        self.port = port
        self.user = user
        self.__password = password
        self.tls = tls

        self.recipients = recipients

        pass

    @_you_shall_not_pass
    def connect(self):
        """
        Method to connect to the SMTP server using the credentials stored
        in the object attributes.
        """
        self.server = smtplib.SMTP(self.ip, self.port)
        if self.tls is True:
            self.server.starttls()
        if self.user is not None and self.__password is not None:
            self.server.login(self.user, self.__password)
        pass

    @_you_shall_not_pass
    def disconnect(self):
        """Method to disconnect from SMTP server."""
        if hasattr(self, 'server') is True:
            self.server.quit()
        pass

    @_you_shall_not_pass
    def send(
        self, subject, text, recipients=None, attachment=None, type='html'
    ):
        """Send regular message to the listed addresses."""
        self.connect()
        sender = self.address
        recipients = recipients or self.recipients
        if recipients is not None:
            if isinstance(recipients, list) is True:
                recipients = ', '.join(recipients)

            message = MIMEMultipart()
            message['From'] = sender
            message['To'] = recipients
            message['Subject'] = subject

            if text is not None:
                if isinstance(text, list) is False:
                    text = [text]
                for item in text:
                    if isinstance(item, MIMEText) is True:
                        part = item
                        message.attach(part)
                    elif isinstance(item, str) is True:
                        part = MIMEText(item, _subtype=type)
                        message.attach(part)

            if attachment is not None:
                if isinstance(attachment, list) is False:
                    attachment = [attachment]
                for item in attachment:
                    filename = os.path.basename(item)
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(open(item, "rb").read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {filename}",
                    )
                    message.attach(part)

            self.server.send_message(message)
        self.disconnect()
        pass

    @_you_shall_not_pass
    def alarm(self):
        """Send alarm message to the listed addresses."""
        subject = f'ALARM in {self.log.app}!'

        text = self.log.header.create()
        text = f'<pre>{text}</pre>'
        text = MIMEText(text, 'html')

        attachment = None
        if self.log.output.file.used is True:
            attachment = self.log.output.file.path

        recipients = self.recipients
        self.send(subject, text, recipients=recipients, attachment=attachment)
        pass
