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
# This logger serves as a filter. Logging events are passed on to other loggers if they are within the
# accepting range of the filter.
#
class FilterLogger(AbstractLogger):


	def __init__(self, logger, minLogLevel):
		super().__init__(None)
		self.__logger = logger
		self.__minLogLevel = minLogLevel
	#



	@staticmethod
	def create(logger, minLogLevel = EnumLogLevel.WARNING):
		assert isinstance(logger, AbstractLogger)

		return FilterLogger(logger, [ int(minLogLevel) ])
	#



	def _log(self, timeStamp, logLevel, textOrException):
		if int(logLevel) >= self.__minLogLevel[0]:
			self.__logger._log(timeStamp, logLevel, textOrException)
	#



	@property
	def minLogLevel(self):
		return self.__minLogLevel[0]
	#



	def setMinLogLevel(self, minLogLevel):
		self.__minLogLevel[0] = minLogLevel
	#



	def _descend(self, logEntryStruct):
		return FilterLogger(self.__logger._descend(logEntryStruct), self.__minLogLevel)
	#



	def clear(self):
		self.__logger.clear()
	#



#






