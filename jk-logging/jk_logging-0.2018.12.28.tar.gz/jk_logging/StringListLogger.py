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
from .AbstractLogMessageFormatter import *
from .LogMessageFormatter import *
from .StringListBuffer import *





#
# This logger writes log data to an internal string list.
#
class StringListLogger(AbstractLogger):


	def __init__(self, idCounter = None, parentID = None, indentationLevel = None, f = None, prefix = None, logMsgFormatter = None):
		super().__init__(idCounter)
		if parentID is None:
			parentID = self._idCounter.next()
		else:
			assert isinstance(parentID, int)
		assert isinstance(f, StringListBuffer)
		assert isinstance(indentationLevel, int)
		if prefix != None:
			assert isinstance(prefix, str)
		self.__logMsgFormatter = DEFAULT_LOG_MESSAGE_FORMATTER if logMsgFormatter is None else logMsgFormatter
		assert isinstance(self.__logMsgFormatter, AbstractLogMessageFormatter)

		self.__f = f
		self._indentationLevel = indentationLevel
		self.__prefix = prefix
	#



	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		if self.__f.isClosed:
			raise Exception("Logger already closed.")

		if bNeedsIndentationLevelAdaption:
			logEntryStruct = list(logEntryStruct)
			logEntryStruct[2] = self._indentationLevel
		lineOrLines = self.__logMsgFormatter.format(logEntryStruct)
		self.__f.print(None, lineOrLines)
	#



	# TODO: provide a more efficient implementation. currently <c>_logi()</c> will be called through <c>_logiAll()</c> so that not single but multiple tests are performed if the logger is already closed.
	def _logiAll(self, logEntryStructList, bNeedsIndentationLevelAdaption):
		if self.__f.closed:
			raise Exception("Logger already closed.")

		super()._logiAll(logEntryStructList, bNeedsIndentationLevelAdaption)
	#



	def _descend(self, logEntryStruct):
		nextID = logEntryStruct[1]
		return StringListLogger(self._idCounter, nextID, self._indentationLevel + 1,
			self.__f, self.__prefix, self.__logMsgFormatter)
	#



	#
	# Create a new instance of this logger.
	#
	# @param		AbstractLogMessageFormatter logMsgFormatter
	#
	@staticmethod
	def create(logMsgFormatter = None):
		logFile = StringListBuffer()
		return StringListLogger(None, None, 0, logFile, None, logMsgFormatter)
	#



	def close(self):
		self.__f.close()
	#



	def closed(self):
		return self.__f.isClosed
	#



	def isClosed(self):
		return self.__f.isClosed
	#



	def clear(self):
		return self.__f.clear()
	#



	def toStr(self):
		return self.__f.getDataAsStr()
	#



	def __str__(self):
		return self.__f.getDataAsStr()
	#



	def toList(self):
		return self.__f.getDataAsList()
	#



#










