import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText


class Emailer(object):

    def __init__(self, msgFrom, msgTo, msgSubject, msgTxt):
        self.msg = MIMEText(msgTxt)
        self.msg['From'] = msgFrom
        self.msg['To'] = msgTo
        self.msg['Subject'] = msgSubject
        self.msgFrom = msgFrom
        self.msgTo = msgTo

    def send(self):
        self.smpt = smtplib.SMTP('cernmx.cern.ch')
        self.smpt.sendmail(self.msgFrom, [self.msgTo], self.msg.as_string())
        self.smpt.quit()

    @staticmethod
    def Send(message, backToNrormal=False):
        subject = 'Everything is back to normal'
        if not backToNrormal:
            subject = 'Failure on cvmfs-lhcbdev'
        s = Emailer('stefan-gabriel.chitic@cern.ch',
                    'stefan-gabriel.chitic@cern.ch',
                    subject,
                    message)
        s.send()

