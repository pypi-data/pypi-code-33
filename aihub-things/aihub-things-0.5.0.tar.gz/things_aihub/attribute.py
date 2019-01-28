from __future__ import print_function
from __future__ import unicode_literals
from .session import MqttSession, CoAPSession
from coapthon.client.helperclient import HelperClient
import json

class Mqtt(MqttSession):
    def upload(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.publish("v1/devices/me/attributes", json.dumps(payload), 1)

    def request(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)

        def on_connect(client, userdata, rc, *extra_params):
            self.client.subscribe('v1/devices/me/attributes/response/+')
            self.client.publish('v1/devices/me/attributes/request/1', json.dumps(payload))

        def on_message(client, userdata, msg):
            print('Received Topic: ', msg.topic, 'Message: ', str(msg.payload))
            self.client.disconnect()
            self.msg = msg

        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.loop_forever()
        return self.msg

    def shared_subscribe(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.subscribe('v1/devices/me/attributes')
        self.client.loop_forever()

class CoAP(CoAPSession):
    def post(self, payload):
        path = "/api/v1/{token}/attributes".format(token=self.token)
        client = HelperClient(server=(self.host, self.port))
        response = client.post(path, json.dumps(payload))
        print(response.pretty_print())
        client.stop()
        return response

    def get(self, attrs, shared=[]):
        path = "/api/v1/{token}/attributes?clientKeys={attrs}&sharedKeys={shared}".format(
            token=self.token, attrs=','.join(attrs), shared=','.join(shared))
        client = HelperClient(server=(self.host, self.port))
        response = client.get(path)
        print(response.pretty_print())
        client.stop()
        return response

    def observe(self, callback=None, timeout=None, **kwargs):
        path = "/api/v1/{token}/attributes".format(token=self.token)

        def client_callback_observe(response):  # pragma: no cover
            print("Callback_observe")

        client = HelperClient(server=(self.host, self.port))
        client.observe(path, client_callback_observe, timeout, *kwargs)