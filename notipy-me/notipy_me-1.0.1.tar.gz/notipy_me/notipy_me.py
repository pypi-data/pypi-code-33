from contextlib import ContextDecorator
import os
import json
from pprint import pprint
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from datetime import datetime

class Notipy(ContextDecorator):
    def __init__(self, path:str=None, name:str=None):
        """Create a new istance of Notipy.
            path:str, optional, path from where to load the config.
            name:str, optional, name of the script.
        """
        super(Notipy, self).__init__()
        self._path = path
        self._name = name if name else "python script"


    def _load(self):
        with open(self._path or "notipy_me.json", "r") as f:
            data = json.load(f)
        self._from = data["from"]
        self._from["port"] = 465 if "port" not in self._from else self._from["port"]
        self._to = [self._from["email"]] if "to" not in data else data["to"]


    def _notify(self, message:str):
        server_ssl = SMTP_SSL(self._from["server"], self._from["port"])
        server_ssl.login(self._from["email"], self._from["password"])
        msg = MIMEText(message, _charset="UTF-8")
        msg["Subject"] = "Your `{name}` has completed!".format(name=self._name)
        msg["To"] = ", ".join(self._to)
        msg["From"] = self._from["email"]
        server_ssl.sendmail(msg["From"], msg["To"], msg.as_string())
        server_ssl.close()
        
    def _build_message(self, success:bool):
        return "Your `{name}` has completed with {status} status, started on {start} and finished on {end}, requiring {delta}.".format(
            status="successful" if success else "failure",
            name=self._name,
            start=self._start,
            end=datetime.now(),
            delta=datetime.now()-self._start    
        )

    def __enter__(self):
        self._start = datetime.now()
        return self

    def __exit__(self, *exc):
        self._load()
        self._notify(self._build_message(exc is None))
        return False