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
from .LogMessageFormatter import *





#
# This logger writes log data to a log file.
#
class SimpleFileLogger(AbstractLogger):



	def __init__(self, filePath, idCounter = None, parentID = None, indentationLevel = 0,
		bAppendToExistingFile = True, bFlushAfterEveryLogMessage = True, fileMode = 0o0600, logMsgFormatter = None):
		super().__init__(idCounter)
		self._indentationLevel = indentationLevel
		if parentID is None:
			parentID = self._idCounter.next()
		self._parentLogEntryID = parentID
		self.__logMsgFormatter = DEFAULT_LOG_MESSAGE_FORMATTER if logMsgFormatter is None else logMsgFormatter
		assert isinstance(self.__logMsgFormatter, AbstractLogMessageFormatter)

		self.__filePath = filePath
		self.__bAppendToExistingFile = bAppendToExistingFile
		self.__bFlushAfterEveryLogMessage = bFlushAfterEveryLogMessage
		if not bAppendToExistingFile:
			if os.path.isfile(filePath):
				os.unlink(filePath)
		self.__f = open(filePath, "a")
		if fileMode is not None:
			os.chmod(filePath, fileMode)
		self.__fileMode = fileMode
	#



	@staticmethod
	def create(filePath, bAppendToExistingFile = True, bFlushAfterEveryLogMessage = True, fileMode = 0o0600, logMsgFormatter = None):
		assert isinstance(filePath, str)
		assert isinstance(bAppendToExistingFile, bool)
		assert isinstance(bFlushAfterEveryLogMessage, bool)
		assert isinstance(fileMode, int)
		if logMsgFormatter != None:
			assert isinstance(logMsgFormatter, AbstractLogMessageFormatter)
		return SimpleFileLogger(filePath, None, None, 0, bAppendToExistingFile, bFlushAfterEveryLogMessage, fileMode, logMsgFormatter)
	#



	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		if self.__f.closed:
			raise Exception("Logger already closed.")

		if bNeedsIndentationLevelAdaption:
			logEntryStruct = list(logEntryStruct)
			logEntryStruct[2] = self._indentationLevel
		lineOrLines = self.__logMsgFormatter.format(logEntryStruct)
		if isinstance(lineOrLines, str):
			self.__f.write(lineOrLines + "\n")
		else:
			for line in lineOrLines:
				self.__f.write(line + "\n")
		if self.__bFlushAfterEveryLogMessage:
			self.__f.flush()
	#



	# TODO: provide a more efficient implementation. currently <c>_logi()</c> will be called through <c>_logiAll()</c> so that not single but multiple tests are performed if the logger is already closed and multiple flushes are performed.
	def _logiAll(self, logEntryStructList, bNeedsIndentationLevelAdaption):
		if self.__f.closed:
			raise Exception("Logger already closed.")

		#for logEntryStruct in logEntryStructList:
		#	lineOrLines = self.__logMsgFormatter.format(logEntryStruct)
		#	if isinstance(lineOrLines, str):
		#		self.__f.write(lineOrLines + "\n")
		#	else:
		#		for line in lineOrLines:
		#			self.__f.write(line + "\n")

		super()._logiAll(logEntryStructList, bNeedsIndentationLevelAdaption)

		#if self.__bFlushAfterEveryLogMessage:
		#	self.__f.flush()
	#



	def _descend(self, logEntryStruct):
		nextID = logEntryStruct[1]
		return SimpleFileLogger(self.__filePath, self._idCounter, nextID, self._indentationLevel + 1,
			self.__bAppendToExistingFile, self.__bFlushAfterEveryLogMessage, self.__fileMode, self.__logMsgFormatter)
	#



	def close(self):
		if not self.__f.closed:
			self.__f.flush()
			self.__f.close()
	#



#



