from __future__ import print_function
from __future__ import unicode_literals
from .session import AdminRestSession
import requests
import json

class Session(AdminRestSession):
    def save_device(self, payload, gateway_token, device_type):
        requst_url = "http://{host}/device/save".format(host=self.host)
        payload['jwtToken'] = self.jwt_token
        payload['gatewayToken'] = gateway_token
        payload['deviceType'] = device_type
        r = requests.post(requst_url, json=payload)
        return r.text

    def delete_device(self, payload, gateway_token):
        requst_url = "http://{host}/device/delete".format(host=self.host)
        payload['jwtToken'] = self.jwt_token
        payload['gatewayToken'] = gateway_token
        r = requests.post(requst_url, json=payload)
        return r.text

    def save_relation(self, payload, gateway_token, device_type):
        requst_url = "http://{host}/relation/save".format(host=self.host)
        payload['jwtToken'] = self.jwt_token
        payload['gatewayToken'] = gateway_token
        payload['deviceType'] = device_type
        r = requests.post(requst_url, json=payload)
        return r.text