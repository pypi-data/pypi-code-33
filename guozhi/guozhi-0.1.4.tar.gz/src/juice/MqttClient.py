#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import time

import paho.mqtt.client as mqtt

from juice.model.PropMessage import PropMessage
from juice.util import Util

EVENT_CONNECT_KEY = "sys_connect"
EVENT_DISCONNECT_KEY = "sys_disconnect"
ID = "id"
FLAG = "flag"
VALUE = "value"


class MqttClient(object):

    def __init__(self, product_code, device_code, secret):
        self.product_code = product_code
        self.device_code = device_code
        self.secret = secret
        self.host = '129.204.42.111'
        self.port = 2883
        self.prop_set_topic = "/{product_code}/{device_code}/prop/set".format(product_code=self.product_code,
                                                                              device_code=self.device_code)
        self.prop_get_topic = "/{product_code}/{device_code}/prop/get".format(product_code=self.product_code,
                                                                              device_code=self.device_code)
        self.prop_report_topic = "/{product_code}/{device_code}/prop/report".format(product_code=self.product_code,
                                                                                    device_code=self.device_code)
        self.sys_info_topic = "/{product_code}/{device_code}/sys/info".format(product_code=self.product_code,
                                                                              device_code=self.device_code)
        self.prop_set_reply_topic = self.prop_set_topic + "_reply"
        self.prop_get_reply_topic = self.prop_get_topic + "_reply"
        self.prop_set_on_message_handler = None
        self.prop_get_on_message_handler = None
        self.client = None

    def __str__(self):
        return "%s,%s,%s,%s,%s" % (self.product_code, self.device_code, self.secret,
                                   self.host, self.port)

    def __on_connect(self, client, userdata, flags, rc):
        message = {
            0: 'Connection successful',
            1: 'Connection refused - incorrect protocol',
            2: 'Connection refused - invalid client',
            3: 'Connection refused - server unavailable',
            4: 'Connection refused - bad username or password',
            5: 'Connection refused - not authorised'
        }
        print(message.get(rc, 'Currently unused'))
        self.client.publish(self.sys_info_topic, json.dumps(Util.get_raspberry_sys_info()), qos=0, retain=False)
        self.client.subscribe(self.prop_get_topic)
        print("Subscribe topic " + self.prop_get_topic)
        self.client.subscribe(self.prop_set_topic)
        print("Subscribe topic " + self.prop_set_topic)

    def __on_message(self, client, userdata, msg):
        json_obj = json.loads(msg.payload.decode("utf-8"))
        print "%s: [topic]:[%s] [Received Message]:[%s]" % (
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), msg.topic, json_obj)
        if ID not in json_obj:
            print "message prop id not exist"
            return

        if FLAG in json_obj:
            message_id = json_obj[ID]
            flag_key = json_obj[FLAG]
            if msg.topic == self.prop_set_topic:
                if flag_key not in self.prop_set_on_message_handler.keys():
                    print "%s set handler not exist" % flag_key
                    return
                else:
                    message = PropMessage(flag_key, json_obj[VALUE])
                    message.id = message_id
                    self.prop_set_on_message_handler[flag_key].execute(self, str(msg.topic), message)
            elif msg.topic == self.prop_get_topic:
                if flag_key not in self.prop_get_on_message_handler.keys():
                    print "%s get handler not exist" % flag_key
                    return
                else:
                    self.prop_get_on_message_handler[flag_key].execute(self, str(msg.topic),
                                                                       str(message_id), str(flag_key))
            elif msg.topic == self.prop_report_topic:
                print json_obj

    def __on_disconnect(self, client, userdata, rc):
        pass

    def __on_publish(self, client, userdata, mid):
        pass

    def __on_subscribe(self, client, userdata, mid, granted_qos):
        pass

    def __on_unsubscribe(self, client, userdata, mid):
        pass

    def __on_log(self, client, userdata, level, buf):
        pass

    def __init(self):
        client_id = self.device_code
        client = mqtt.Client(client_id + str(time.time()))
        client.username_pw_set(self.device_code, self.secret)
        client.connect(self.host, self.port, 60)
        client.reconnect_delay_set(min_delay=1, max_delay=120)
        # client.on_connect = self.on_connect
        # client.on_message = self.on_message
        # client.on_disconnect = self.on_disconnect
        # client.on_publish = self.on_publish
        # client.on_subscribe = self.on_subscribe
        # client.on_unsubscribe = self.on_unsubscribe
        # client.on_log = self.on_log
        client.on_message = self.__on_message
        client.on_connect = self.__on_connect
        self.client = client

    def __subscriber(self):
        self.client.loop_forever()

    def prop_reply(self, topic, prop_message):
        print "%s: [topic]:[%s] [Send Message]:[%s]" % (
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), topic, prop_message)
        self.client.publish(topic, str(prop_message), qos=0, retain=False)

    def prop_reporter(self, message):
        print "prop_reporter publish topic:%s" % self.prop_report_topic
        self.client.publish(self.prop_report_topic, message, qos=0, retain=False)

    def init(self):
        self.__init()
        self.__subscriber()

    @property
    def get_message(self):
        return self.prop_get_on_message_handler

    @property
    def set_message(self):
        return self.prop_set_on_message_handler

    @get_message.setter
    def get_message(self, handler_dict):
        self.prop_get_on_message_handler = handler_dict

    @set_message.setter
    def set_message(self, handler_dict):
        self.prop_set_on_message_handler = handler_dict
