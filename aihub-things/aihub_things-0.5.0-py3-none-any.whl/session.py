from __future__ import print_function
from __future__ import unicode_literals
import paho.mqtt.client as mqtt
from coapthon.client.helperclient import HelperClient
import json

class MqttSession(object):
    def __init__(self, token, host, port=1883, keepalive=60):
        self.host = host
        self.token = token
        self.port = port
        self.keepalive = 60
        self.client = mqtt.Client()
        self.client.username_pw_set(token)

class RestHttpSession(object):
    def __init__(self, device_id, host, jwt_token):
        self.device_id = device_id
        self.host = host
        self.token = jwt_token

class AdminRestSession(object):
    def __init__(self, host, jwt_token):
        self.host = host
        self.jwt_token = jwt_token


class DeviceHttpSession(object):
    pass

class CoAPSession(object):
    def __init__(self, host, token, port=5683, timeout=1):
        self.host = host
        self.token = token
        self.port = port
        self.timeout = timeout
