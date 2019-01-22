#!/usr/bin/env python
# -*- coding:utf-8 -*-


class PropSetHandler(object):

    def __init__(self):
        self.id = None
        self.client = None
        self.topic = None
        self.reply_topic = None
        self.reply_message = None

    def _reply(self):
        if self.reply_message is None:
            raise ValueError('reply message is not None')
        else:
            self.reply_message.id = self.id
            self.client.prop_reply(self.reply_topic, self.reply_message)

    def execute(self, client, topic, set_prop_message):
        self.id = set_prop_message.id
        self.client = client
        self.topic = topic
        self.reply_topic = topic + "_reply"
        self.handle(set_prop_message)
        self._reply()

    def reply(self, reply_message):
        """
        上行消息,不允许重写
        :param reply_message: PropMessage类型，包含flag,value
        :return:
        """
        self.reply_message = reply_message

    def handle(self, set_prop_message):
        """
        云端下发(下行)设置属性消息,需要重写接收set_prop_message进行处理
        :param set_prop_message: PropMessage类型，包含flag,value
        """
        pass
