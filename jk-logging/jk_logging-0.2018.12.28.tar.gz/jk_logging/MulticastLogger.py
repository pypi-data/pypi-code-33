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
# This logger will broadcast log messages to additional loggers.
#
class MulticastLogger(AbstractLogger):



	def __init__(self, idCounter = None, loggerList = None, indentationLevel = 0, parentLogEntryID = 0):
		super().__init__(idCounter)
		self._indentationLevel = indentationLevel
		self._parentLogEntryID = parentLogEntryID

		self.__loggerList = []
		if loggerList is not None:
			if isinstance(loggerList, AbstractLogger):
				self.__loggerList.append(loggerList)
			elif isinstance(loggerList, (tuple, list)):
				for item in loggerList:
					if isinstance(item, AbstractLogger):
						self.__loggerList.append(item)
					else:
						raise Exception("Invalid object found in logger list: " + str(type(item)))
			else:
				raise Exception("Invalid logger list: " + str(type(loggerList)))

	#



	@staticmethod
	def create(*argv):
		return MulticastLogger(loggerList = argv)

	#



	def addLogger(self, logger):
		assert isinstance(logger, AbstractLogger)
		self.__loggerList.append(logger)

	#



	def removeLogger(self, logger):
		assert isinstance(logger, AbstractLogger)
		self.__loggerList.remove(logger)

	#



	def removeAllLoggers(self):
		self.__loggerList = []

	#



	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		for logger in self.__loggerList:
			logger._logi(logEntryStruct, True)

	#



	def _descend(self, logEntryStruct):
		nextID = logEntryStruct[1]
		newList = []
		for logger in self.__loggerList:
			newList.append(logger._descend(logEntryStruct))
		return MulticastLogger(self._idCounter, newList, self._indentationLevel + 1, nextID)

	#



	def clear(self):
		for logger in self.__loggerList:
			logger.clear()

	#



	def __str__(self):
		return "<MulticastLogger(" + hex(id(self)) + ", " + str(self.__loggerList) + ")>"

	#



	def __repr__(self):
		return "<MulticastLogger(" + hex(id(self)) + ", " + str(self.__loggerList) + ")>"

	#



	def close(self):
		for logger in self.__loggerList:
			logger.close()

	#



#



