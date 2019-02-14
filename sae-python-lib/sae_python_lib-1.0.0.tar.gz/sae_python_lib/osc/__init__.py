#!/usr/bin/python3
# coding=utf-8

from pythonosc import udp_client

# See "http://write.flossmanuals.net/pure-data/osc/" for PureData implementation
class OSC():
	def __init__(self, ip='127.0.0.1', port=57120):
		self.ip = ip
		self.port = port
		self.client = udp_client.SimpleUDPClient(self.ip, self.port)

	def sendMessage(self, tag="/s_new", args=["string", 1, 0.009]):
		self.client.send_message(tag, args)
		return self