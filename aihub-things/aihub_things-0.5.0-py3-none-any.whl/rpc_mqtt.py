from __future__ import print_function
from __future__ import unicode_literals
import paho.mqtt.client as mqtt
from .session import MqttSession
import requests
import json

class Session(MqttSession):
    #rpc from client side
    def request(self, payload):
        self.client.connect(self.host, self.port, self.keepalive)

        def on_connect(client, userdata, rc, *extra_params):
            self.client.subscribe('v1/devices/me/rpc/response/+')
            self.client.publish('v1/devices/me/rpc/request/1', json.dumps(payload))

        def on_message(client, userdata, msg):
            print('Received Topic: ', msg.topic, 'Message: ', str(msg.payload))
            self.client.disconnect()
            self.msg = msg

        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.loop_forever()
        return self.msg

    #response when rpc from server side
    def response(self, msg, payload):
        self.client.publish(msg.topic.replace('request', 'response'), json.dumps(payload), 1)

    #rpc from server side 
    def listen_request(self):
        self.client.connect(self.host, self.port, self.keepalive)

        def on_connect(client, userdata, rc, *extra_params):
            self.client.subscribe('v1/devices/me/rpc/request/+')
            
            if hasattr(self, 'user_on_connect_action'):
                self.user_on_connect_action(rc)
           
            print("Start to listen Server-side RPC")

        def on_message(client, userdata, msg):
            print('Received Topic: ', msg.topic, 'Message: ', str(msg.payload))
            
            if hasattr(self, 'user_on_message_action'):
                self.user_on_message_action(msg)

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Connection Closed")

if __name__ == "__main__":
    s = Session(host='192.168.1.71', token='AU700o0tKRNby9sdAwCZ')

    def on_message(msg):
        print("on message")

    def on_connect(rc):
        print("on connect")

    s.user_on_message_action = on_message
    s.user_on_connect_action = on_connect
    s.listen_request()
    