from __future__ import print_function
from __future__ import unicode_literals
from .session import MqttSession, CoAPSession
from coapthon.client.helperclient import HelperClient
import json

class Mqtt(MqttSession):
    def upload(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.publish("v1/devices/me/telemetry", json.dumps(payload), 1)

class CoAP(CoAPSession):
    def post(self, payload):
        path = "/api/v1/{token}/telemetry".format(token=self.token)
        client = HelperClient(server=(self.host, self.port))
        response = client.post(path, json.dumps(payload))
        print(response.pretty_print())
        client.stop()
        return response

class MqttGateway(MqttSession):
    def upload(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.publish("v1/gateway/telemetry", json.dumps(payload), 1)
