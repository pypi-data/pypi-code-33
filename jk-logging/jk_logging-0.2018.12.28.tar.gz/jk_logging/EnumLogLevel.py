#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os

from enum import Enum




class EnumLogLevel(Enum):
	TRACE = 10, 'TRACE'
	DEBUG = 20, 'DEBUG'
	NOTICE = 30, 'NOTICE'
	INFO = 40, 'INFO'
	STDOUT = 41, 'STDOUT'
	SUCCESS = 50, 'SUCCESS'
	WARNING = 60, 'WARNING'
	ERROR = 70, 'ERROR'
	STDERR = 71, 'STDERR'
	EXCEPTION = 80, 'EXCEPTION'

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value_ = value
		member.fullname = name
		return member

	def __int__(self):
		return self._value_

	def __str__(self):
		return self.fullname

	def toJSON(self):
		return self._value_

	#
	# This method converts a string or integer representing a log level back to an enumeration instance.
	#
	@staticmethod
	def parse(data):
		if isinstance(data, int):
			return EnumLogLevel.__dict__["_value2member_map_"][data]
		elif isinstance(data, str):
			if data in EnumLogLevel.__dict__["_member_names_"]:
				return EnumLogLevel.__dict__[data]
		raise Exception("Unrecognized enumeration value: " + str(data))




