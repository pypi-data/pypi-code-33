#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import traceback
import sys
import abc

import sh

from .EnumLogLevel import *
from .AbstractLogger import *





#
# This object represents a string list buffer.
#
class StringListBuffer(object):

	#
	# Constructor method.
	#
	def __init__(self):
		self.__list = []
	#



	#
	# Write one or more text lines to the log file.
	#
	# @param		str prefix				If not <c>None</c> this text is prepended to the log file.
	# @param		mixed lineOrLines		A single text string or a list of text lines to write. Don't specify <c>None</c> here.
	#
	def print(self, prefix, lineOrLines):
		if self.__list is None:
			raise Exception("File already closed!")

		if isinstance(lineOrLines, str):
			if prefix is None:
				self.__list.append(lineOrLines)
			else:
				self.__list.append(prefix + lineOrLines)
		else:
			if prefix is None:
				for line in lineOrLines:
					self.__list.append(line)
			else:
				for line in lineOrLines:
					self.__list.append(prefix + line)
	#



	#
	#
	#
	def getDataAsList(self):
		return self.__list
	#



	#
	#
	#
	def getDataAsStr(self):
		ret = ""
		for line in self.__list:
			ret += line + "\n"
		return ret
	#



	#
	# Close the file.
	#
	def close(self):
		self.__list = None
	#



	#
	# Checks if the file is closed.
	#
	# @return	bool		Returns <c>true</c> if the file is already closed.
	#
	@property
	def isClosed(self):
		return self.__list is None
	#



	#
	# Checks if the file is closed.
	#
	# @return	bool		Returns <c>true</c> if the file is already closed.
	#
	@property
	def closed(self):
		return self.__list is None
	#



	#
	# Removes all data.
	#
	def clear(self):
		if self.__list is None:
			return
		self.__list = []
	#



#









