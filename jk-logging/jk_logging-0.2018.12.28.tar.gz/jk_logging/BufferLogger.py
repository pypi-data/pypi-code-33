#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import traceback
import sys
import abc
import datetime

import sh

from .EnumLogLevel import *
from .AbstractLogger import *





#
# This logger will buffer log messages in an internal array. Later this data can be forwarded to
# other loggers, f.e. in order to store them on disk.
#
class BufferLogger(AbstractLogger):



	def __init__(self, idCounter = None, parentID = None, indentLevel = 0, logItemList = None):
		super().__init__(idCounter)
		self._indentationLevel = indentLevel
		if logItemList is None:
			self.__list = []
		else:
			self.__list = logItemList
		if parentID is None:
			parentID = self._idCounter.next()
		self._parentLogEntryID = parentID
	#



	@staticmethod
	def __convertRawLogData(items):
		ret = []
		for item in items:
			item = list(item)
			item[5] = EnumLogLevel.parse(item[5])
			if item[0] == "txt":
				pass
			elif item[0] == "ex":
				pass
			elif item[0] == "desc":
				item[7] = BufferLogger.__convertRawLogData(item[7])
			else:
				raise Exception("Implementation Error!")
			ret.append(item)
		return ret
	#



	@staticmethod
	def create(jsonRawData = None):
		if jsonRawData != None:
			jsonRawData = BufferLogger.__convertRawLogData(jsonRawData)
			return BufferLogger(None, None, 0, jsonRawData)
		return BufferLogger()
	#



	"""
	#
	# Return a list of strings that contains the data stored in this logger.
	#
	# @return		string[]		Returns an array of strings ready to be written to the console or a file.
	#
	def getBufferDataAsStrList(self):
		ret = []
		for logEntryStruct in in self.__list:
			...
		return ret
	"""




	"""
	#
	# Return a single string that contains the data stored in this logger.
	#
	# @return		string		Returns a single string ready to be written to the console or a file.
	#
	def getBufferDataAsStr(self):
		s = ''
		for logEntryStruct in in self.__list:
			...
		return s
	"""



	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		if bNeedsIndentationLevelAdaption:
			logEntryStruct = list(logEntryStruct)
			logEntryStruct[2] = self._indentationLevel
		self.__list.append(logEntryStruct)
	#



	def _descend(self, logEntryStruct):
		nextID = logEntryStruct[1]
		newList = logEntryStruct[7]
		return BufferLogger(self._idCounter, nextID, self._indentationLevel + 1, newList)
	#



	#
	# Forward the log data stored in this logger to another logger.
	#
	# @param		AbstractLogger logger			Another logger that will receive the log data.
	# @param		bool bClear						Clear buffer after forwarding all log data.
	#
	def forwardTo(self, logger, bClear = False):
		assert isinstance(logger, AbstractLogger)
		logger._logiAll(self.__list, True)
		if bClear:
			self.__list = []
	#



	def clear(self):
		self.__list = []
	#



	def getDataAsJSON(self):
		return self.__getJSONData(self.__list)
	#



	def __getJSONData(self, items):
		ret = []
		for item in items:
			item2 = list(item)
			item2[5] = int(item2[5])
			if item2[0] == "txt":
				pass
			elif item2[0] == "ex":
				pass
			elif item2[0] == "desc":
				item2[7] = self.__getJSONData(item2[7])
			else:
				raise Exception("Implementation Error!")
			ret.append(item2)
		return ret
	#



	def getDataAsPrettyJSON(self):
		return self.__getPrettyJSONData(self.__list)
	#



	def __stackTraceElementToPrettyJSONData(self, stackTraceItem):
		return {
			"file": stackTraceItem[0],
			"line": stackTraceItem[1],
			"module": stackTraceItem[2],
			"sourcecode": stackTraceItem[3],
		}
	#

	def __getPrettyJSONData(self, items):
		ret = []
		for item in items:
			item2 = list(item)
			t = datetime.datetime.fromtimestamp(item2[4])
			jsonLogEntry = {
				"type": item2[0],
				"id": item2[1],
				"indent": item2[2],
				"timestamp": {
					"t": item2[4],
					"year": t.year,
					"month": t.month,
					"day": t.day,
					"hour": t.hour,
					"minute": t.minute,
					"second": t.second,
					"ms": t.microsecond // 1000,
					"us": t.microsecond % 1000,
				},
				"loglevel": str(item2[5]),
				"logleveln": int(item2[5]),
			}
			if item2[0] == "txt":
				jsonLogEntry["text"] = item2[6]
			elif item2[0] == "ex":
				jsonLogEntry["exception"] = item2[6]
				jsonLogEntry["text"] = item2[7]
				jsonLogEntry["stacktrace"] = [ self.__stackTraceElementToPrettyJSONData(x) for x in item2[8] ] if item2[8] else None
			elif item2[0] == "desc":
				jsonLogEntry["text"] = item2[6]
				jsonLogEntry["children"] = self.__getPrettyJSONData(item2[7])
			else:
				raise Exception("Implementation Error!")
			ret.append(jsonLogEntry)
		return ret
	#



	def __str__(self):
		return "<BufferLogger(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#



	def __repr__(self):
		return "<BufferLogger(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#



#






