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
from .RollOverLogFile import *





#
# This logger writes log data to a log file. Log file rotation is supported.
#
class FileLogger(AbstractLogger):


	def __init__(self, idCounter = None, parentID = None, indentationLevel = None, f = None, prefix = None, logMsgFormatter = None):
		super().__init__(idCounter)
		if parentID is None:
			parentID = self._idCounter.next()
		else:
			assert isinstance(parentID, int)
		assert isinstance(f, RollOverLogFile)
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
		return FileLogger(self._idCounter, nextID, self._indentationLevel + 1,
			self.__f, self.__prefix, self.__logMsgFormatter)

	#



	#
	# Create a new instance of this logger.
	#
	# @param		str filePath									The path of the file to write the log data to. If <c>rollOverMode</c> is not <c>None</c>
	#																you need to use the following shortcuts within the file path to be filled in with date and
	#																time values:
	#																* %Y - year (f.e. 2017with date and
	#																* %m - month (f.e. 08)
	#																* %d - day (f.e. 02)
	#																* %H - hour (f.e. 03)
	#																* %M - minute (f.e. 49)
	#																* %S - second (f.e. 07)
	#																All values used in the pattern elements are padded with zeros.
	# @param		str rollOverMode								Either specify <c>None</c> if no roll-over should be used. Otherwise
	#																specify either "second", "minute", "hour", "day" or "month".
	# @param		bool bAppendToExistingFile						If <c>True</c> a possibly already existing file will be reused, data will
	#																be appended. If <c>False</c> the file will be recreated if it already exists.
	# @param		bool bFlushAfterEveryWrite						If <c>True</c> perform a flush after every write.
	# @param		int fileMode									If not <c>None</c> <c>chmod()</c> will be called with these file modes specified here.
	# @param		AbstractLogMessageFormatter logMsgFormatter		A log message formatter. If <c>None</c> is specified the default one is used.
	#
	@staticmethod
	def create(filePath, rollOver, bAppendToExistingFile = True, bFlushAfterEveryLogMessage = True, fileMode = None,
		logMsgFormatter = None):
		assert isinstance(filePath, str)
		if rollOver is not None:
			assert rollOver in ["second", "minute", "hour", "day", "month", "none"]
			if rollOver == "none":
				rollOver = None
		assert isinstance(bAppendToExistingFile, bool)
		assert isinstance(bFlushAfterEveryLogMessage, bool)
		assert isinstance(fileMode, (type(None), int))

		logFile = RollOverLogFile(filePath, rollOver, bAppendToExistingFile, bFlushAfterEveryLogMessage, fileMode)
		return FileLogger(None, None, 0, logFile, None, logMsgFormatter)
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



#








