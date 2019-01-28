from __future__ import print_function
from __future__ import unicode_literals
import paho.mqtt.client as mqtt
from coapthon.client.helperclient import HelperClient
from .session import MqttSession, CoAPSession
import requests
import json

class Session(CoAPSession):
    def observe(self, callback=None, timeout=None):
        path = "/api/v1/{token}/rpc".format(token=self.token)

        def default_callback(response):
            print(response.pretty_print())

        if callback == None:
            callback = default_callback

        client = HelperClient(server=(self.host, self.port))
        client.observe(path, callback, timeout)

    def post(self, payload):
        path = "/api/v1/{token}/rpc".format(token=self.token)
        client = HelperClient(server=(self.host, self.port))
        response = client.post(path, json.dumps(payload))
        print(response.pretty_print())
        client.stop()
        return response