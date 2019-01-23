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
# This logger will buffer log messages in an array.
#
class BufferLogger(AbstractLogger):



	def __init__(self, indentLevel = 0, prefix = "", logItemList = None):
		self.__level = indentLevel
		self.__prefix = prefix
		if logItemList is None:
			self.__list = []
		else:
			self.__list = logItemList



	#
	# Return a list of strings that contains the data stored in this logger.
	# Standard formatting is used for output.
	#
	# @return		string[]		Returns an array of strings ready to be written to the console or a file.
	#
	def getBufferDataAsStrList(self):
		ret = []
		for (timeStamp, logLevel, textOrException) in self.__list:
			lineOrLines = self._logEntryToStringOrStringList(timeStamp, logLevel, textOrException)
			if isinstance(lineOrLines, str):
				ret.append(self.__prefix + lineOrLines)
			else:
				for line in lineOrLines:
					ret.append(self.__prefix + line)
		return ret



	#
	# Return a list of tuples that contains the data stored in this logger.
	#
	# @return		tuple[]		Returns an array of tuples. Each tuple will contain the following fields:
	#							* int timeStamp : The time stamp since Epoch in seconds.
	#							* EnumLogLevel logLevel : The log level of this log entry.
	#							* string|Exception textOrException : A log message or an execption object.
	#
	def getBufferDataAsTupleList(self):
		return self.__list



	#
	# Return a single string that contains the data stored in this logger.
	# Standard formatting is used for output.
	#
	# @return		string		Returns a single string ready to be written to the console or a file.
	#
	def getBufferDataAsStr(self):
		s = ''
		for (timeStamp, logLevel, textOrException) in self.__list:
			lineOrLines = self._logEntryToStringOrStringList(timeStamp, logLevel, textOrException)
			if isinstance(lineOrLines, str):
				s += self.__prefix + lineOrLines + "\n"
			else:
				for line in lineOrLines:
					s += self.__prefix + line + "\n"
		return s



	def _log(self, timeStamp, logLevel, textOrException):
		self.__list.append((timeStamp, logLevel, textOrException))



	def descend(self, text):
		self._log(time.time(), EnumLogLevel.INFO, text)
		return BufferLogger(self.__level + 1, self.__prefix + "\t", self.__list)



	#
	# Forward the log data stord in this logger to another logger.
	#
	# @param		AbstractLogger logger			Another logger that will receive the log data.
	#
	def forwardTo(self, logger, bClear = False):
		assert isinstance(logger, AbstractLogger)

		logger._logAll(self.__list)

		if bClear:
			self.__list = []



	def clear(self):
		self.__list = []







