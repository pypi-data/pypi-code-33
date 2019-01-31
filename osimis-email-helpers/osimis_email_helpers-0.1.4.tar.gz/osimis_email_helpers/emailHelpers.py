from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from osimis_email_helpers.exceptions import *

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

        try:
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

        except Exception as ex:
            raise EmailHelpersException(msg = "Error in sendMail method", innerException = ex)


if __name__ == "__main__":

    # Allow to pass file name in order to test script in dev
    parser = argparse.ArgumentParser("send a test e-mail")

    parser.add_argument('-t', '--to', help = "e-mail address to send to.")
    parser.add_argument('-f', '--fromAddress', help = "from e-mail address.")
    parser.add_argument('-h', '--hostname', help = "smtp hostname.")
    parser.add_argument('-p', '--port', help = "smtp port.")
    parser.add_argument('-b', '--body', help = "email body.")
    parser.add_argument('-s', '--subject', help = "email subject.")
    args = parser.parse_args()

    emailSender = EmailHelpers(
        smtpHostname = args.smtp,
        smtpPort = int(args.port),
        fromAddress = args.fromAddress,
        toAddresses = [args.to]
    )

    emailSender.sendMail(body = args.body, subject = args.subject)
