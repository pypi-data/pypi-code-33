import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import html2text

from hs_infra.meta_classes.singleton_meta_class import Singleton


class BaseEmailAdapter(metaclass=Singleton):
    """https://docs.python.org/3/library/email.examples.html"""

    def __init__(self, smtp_username, smtp_password=None, host='', port=0, context=None):
        """ See 'ssl' library for creating context:
        context = ssl._create_stdlib_context(certfile=certfile, keyfile=keyfile)"""
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.host = host
        self.port = port
        self.context = context

    def send_mail(self, sender, recipient, subject, plain=None, html=None):
        if self.context:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls(self.context)
        else:
            server = smtplib.SMTP_SSL(self.host, self.port)
        server.login(self.smtp_username, self.smtp_password)
        self._send_mail(server, sender, recipient, subject, plain, html)
        server.quit()

    def _send_mail(self, server, sender, recipient, subject, plain=None, html=None):
        if html:
            if not plain:
                plain = html2text.html2text(html)
            msg = self._multipart_mail_msg(plain, html)
        else:
            assert isinstance(plain, str)
            msg = self._plain_mail_msg(plain)

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        server.sendmail(sender, [recipient], msg.as_string())

    def _multipart_mail_msg(self, plain, html) -> MIMEBase:
        part1 = MIMEText(plain, 'plain')
        part2 = MIMEText(html, 'html')
        msg = MIMEMultipart("alternative")
        msg.attach(part1)
        msg.attach(part2)
        return msg

    def _plain_mail_msg(self, plain) -> MIMEBase:
        msg = MIMEText(plain)
        return msg


if __name__ == '__main__':
    sender = 'info@webcentriq.com'
    password = 'Webcentriq@77'
    recipient = 'ehsun.zz@gmail.com'
    host = 'smtp.zoho.com'
    # Create message
    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = """\
    <html>
      <head></head>
      <body>
        <p><h1>Hi!</h1><br>
           How are you?<br>
           Here is the <a href="http://www.python.org">link</a> you wanted.
        </p>
      </body>
    </html>
    """

    adapter = BaseEmailAdapter(sender, password, host, 465)
    adapter.send_mail(sender, recipient, 'whats wrong with infra', html=html)
