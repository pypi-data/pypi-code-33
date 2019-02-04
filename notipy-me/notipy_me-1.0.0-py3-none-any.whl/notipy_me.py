from contextlib import ContextDecorator
import os
import json
from pprint import pprint
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from datetime import datetime

class Notipy(ContextDecorator):
    def __init__(self, path:str=None):
        super(Notipy, self).__init__()
        with open(path or "notipy_me.json", "r") as f:
            data = json.load(f)
        self._from = data["from"]
        self._from["port"] = 465 if "port" not in self._from else self._from["port"]
        self._to = [self._from["email"]] if "to" not in data else data["to"]

    def _notify(self, message:str):
        server_ssl = SMTP_SSL(self._from["server"], self._from["port"])
        server_ssl.login(self._from["email"], self._from["password"])
        msg = MIMEText(message, _charset="UTF-8")
        msg["Subject"] = "Script has completed!"
        msg["To"] = ", ".join(self._to)
        msg["From"] = self._from["email"]
        server_ssl.sendmail(msg["From"], msg["To"], msg.as_string())
        server_ssl.close()
        
    def _build_message(self, success:bool):
        return "The script has completed with {status} status, started on {start} and finished on {end}, requiring {delta}.".format(
            status="successful" if success else "failure",
            start=self._start,
            end=datetime.now(),
            delta=datetime.now()-self._start    
        )

    def __enter__(self):
        self._start = datetime.now()
        return self

    def __exit__(self, *exc):
        self._notify(self._build_message(exc is None))
        return False