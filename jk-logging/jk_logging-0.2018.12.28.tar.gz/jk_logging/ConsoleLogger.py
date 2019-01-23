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
# This logger will broadcast log messages to additional loggers.
#
class ConsoleLogger(AbstractLogger):



	def __init__(self, idCounter = None, parentID = None, indentationLevel = 0, printToStdErr = False, logMsgFormatter = None):
		super().__init__(idCounter)
		self._indentationLevel = indentationLevel
		if parentID is None:
			parentID = self._idCounter.next()
		self._parentLogEntryID = parentID
		self.__logMsgFormatter = DEFAULT_LOG_MESSAGE_FORMATTER if logMsgFormatter is None else logMsgFormatter

		self.__print = self.__eprint if printToStdErr else print
		self.__printToStdErr = printToStdErr
	#



	@staticmethod
	def create(printToStdErr = False, logMsgFormatter = None):
		return ConsoleLogger(printToStdErr = printToStdErr, logMsgFormatter = logMsgFormatter)
	#



	def __eprint(self, *args, **kwargs):
		print(*args, file=sys.stderr, **kwargs)
	#



	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		if bNeedsIndentationLevelAdaption:
			logEntryStruct = list(logEntryStruct)
			logEntryStruct[2] = self._indentationLevel
		lineOrLines = self.__logMsgFormatter.format(logEntryStruct)
		if isinstance(lineOrLines, str):
			self.__print(lineOrLines)
		else:
			for line in lineOrLines:
				self.__print(line)
	#



	def _descend(self, logEntryStruct):
		nextID = logEntryStruct[1]
		return ConsoleLogger(self._idCounter, nextID, self._indentationLevel + 1, self.__printToStdErr, self.__logMsgFormatter)
	#



	def __str__(self):
		return "<ConsoleLogger(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#



	def __repr__(self):
		return "<ConsoleLogger(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#



#






