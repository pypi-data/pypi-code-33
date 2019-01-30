from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib, argparse, os, typing

"""
A simple library to make email sending easy:

This library is useful in customer side scripts (syncher for Lify,...) when
the customer allow access to its smtp server.

Just instanciate EmailHelpers class with right parameters and then
call 'sendMail' method when an email alert is needed.
"""

class EmailHelpers:

    def __init__(self, smtpHostname: str,
                 smtpPort: int,
                 fromAddress: str,
                 toAddresses: typing.List[str],
                 ccAddresses: typing.List[str] = [],
                 smtpLogin: str = None,
                 smtpPassword: str = None,
                 debugMode: bool = False
                 ):
        '''
        :param smtpHostname: something like 'mail.myhospital.be'
        :param smtpPort: something like '25'
        :param fromAddress: something like noreply@lify.io
        :param toAddresses: a list with elements like support@myhospital.be
        :param ccAddresses: a list with elements like ops@lify.io
        :param smtpLogin: optionnal
        :param smtpPassword: optionnal
        :param debugMode: if 'True', email won't be really sent
        '''
        self._smtpHostname = smtpHostname
        self._smtpPort = smtpPort
        self._fromAddress = fromAddress
        self._toAddresses = toAddresses
        self._ccAddresses = ccAddresses
        self._smtpLogin = smtpLogin
        self._smtpPassword = smtpPassword
        self._debugMode = debugMode

    def sendMail(self, body: str, subject: str):
        """
        Sends a mail.
        :param body: email body
        :param subject: email subject
        :return:
        """

        msg = MIMEMultipart()
        msg['From'] = self._fromAddress
        msg['To'] = ', '.join(self._toAddresses)
        msg['Cc'] = ', '.join(self._ccAddresses)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(self._smtpHostname, self._smtpPort)

        if self._smtpLogin and self._smtpPassword is not None:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self._smtpLogin, self._smtpPassword)
        text = msg.as_string()
        if self._debugMode is not True:
            server.sendmail(self._fromAddress, self._toAddresses + self._ccAddresses, text)
        server.quit()


if __name__ == "__main__":

    # Allow to pass file name in order to test script in dev
    parser = argparse.ArgumentParser("send a test e-mail")

    parser.add_argument('-t', '--to', help = "e-mail address to send to.", default = "abc@def.com")
    args = parser.parse_args()

    emailSender = EmailHelpers(
        smtpHostname = "mail.abc.com",
        smtpPort = 25,
        fromAddress = "noreply@def.com",
        toAddresses = [args.to]
    )

    emailSender.sendMail(body = "Hello\r\n This is the body of the test mail.", subject = "this is the mail subject")
