import smtplib
import os
import os.path as op
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders

class SendMail():

    def __init__(self, mail_sender, password):
        self.mail_sender = mail_sender
        self.password = password


    def send_message(self, subject, message, receivers):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.mail_sender
            msg['To'] = receivers
            msg['Subject'] = subject

            body = message
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.mail_sender, self.password)
            text = msg.as_string()
            server.sendmail(self.mail_sender, receivers, text)
            server.quit()
        except Exception as e:
            print('Error: could not send mail because of {0}'.format(e))


    def send_attachment(self, subject, message, receivers, attachment):
        try:
            print(attachment)
            outer = MIMEMultipart()
            outer['From'] = self.mail_sender
            outer['To'] = receivers
            outer['Subject'] = subject

            # Add content to message
            body = message
            outer.attach(MIMEText(body, 'plain'))

            # Add attachment to message
            with open(attachment, 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
            outer.attach(msg)

            # Send message
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.mail_sender, self.password)
            text = outer.as_string()
            server.sendmail(self.mail_sender, receivers, text)
            server.quit()
        except Exception as e:
            print('Error: could not send mail because of {0}'.format(e))
