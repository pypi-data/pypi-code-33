import smtplib

class email_io(object):

    _email_username = "noreply.runsonaether@gmail.com"
    _email_password = "textbayrunsonaether"
    _email_smtp_host = "smtp.gmail.com:587"
    _email_address_host = "gmail.com"

    def __init__(self):
        self._server = smtplib.SMTP(self._email_smtp_host)
        self._server.ehlo()
        self._server.starttls()
        self._server.login(self._email_username, self._email_password)

    def send(self, to_address, body_msg, subject_line="Automatic Message From Aether Platform"):
        msg = "\r\n".join([
            "From: {}".format(self._email_username),
            "To: {}".format(to_address),
            "Subject: {}".format(subject_line),
            "",
            "{}".format(body_msg)
        ])
        self._server.sendmail("{}@{}".format(self._email_username, self._email_address_host),
                              to_address, msg)
