#!/usr/bin/python3
# coding=utf-8

from pythonosc import udp_client
from threading import Thread
import numpy as np

# Example name for serial_names: b'a1\r\n'
class Arduino(Thread):
	def __init__(self, port='/dev/cu.usbmodem1411', baud_rate=9600, serial_names=[]):
		Thread.__init__(self)
		self.port = port
		self.baud_rate = baud_rate
		self.serial_names = serial_names
		self.values = np.zeros(len(self.serial_names))
		self.data = b''
		self.old_data = b''
		self.isRunning = False
		self.daemon = False
		self.ser = None
		try:
			self.ser = serial.Serial(self.port, self.baud_rate)
		except:
			print("Failed to open Serial Port: " + self.port)
		#self.serial_names = [b'a1\r\n', b'a2\r\n', b'a3\r\n', b'a4\r\n', b'a5\r\n', b'mn\r\n', b'br\r\n', b'ba\r\n']
			
	def run(self):
		while True:
			self.old_data = self.data
			self.data = self.ser.readline()
			for i in range(len(self.values)):
				if self.old_data == self.sensor_names[i]:
					self.values[i] = float(self.data[:-4]) / 1023.0