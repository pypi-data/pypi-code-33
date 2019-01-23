import json
import rfc3339
from datetime import datetime
import pytz
class InstanceInfo:
    def __init__(self,name="stat-api",startupAt=None,version_file=None):
        self.name=name
        self.startupAt=startupAt
        self.date = startupAt
        with open(version_file) as ss:
            s = json.load(ss)
        self.info=s

    def toMap(self):
        dt = datetime.now(pytz.UTC)
        return {'name': self.name,'startupAt': self.startupAt.strftime('%Y-%m-%dT%H:%M:%SZ'),"date":dt.strftime('%Y-%m-%dT%H:%M:%SZ'),'info':self.info}

