from __future__ import print_function
from __future__ import unicode_literals
from .session import RestHttpSession
import requests
import json

class Session(RestHttpSession):
    def request(self, payload, type=1):
        type = "oneway" if type == 1 else "twoway"
        requst_url = "http://{host}/api/plugins/rpc/{type}/{id}".format(host=self.host,  type=type, id=self.device_id)
        headers = {"X-Authorization": "Bearer " + self.token}
        r = requests.post(requst_url, json=payload, headers=headers)

        if type=="oneway":
            return r.status_code
        else:
            return r.status_code, r.text