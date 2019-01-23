#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime

from enum import Enum

from .EnumLogLevel import EnumLogLevel
from .AbstractLogMessageFormatter import AbstractLogMessageFormatter





#
# This is a default formatter for log messages. It produces human readable output for log messages.
#
class ColoredLogMessageFormatter(AbstractLogMessageFormatter):

	class EnumOutputMode(Enum):
		VERY_SHORT = 0
		SHORTED = 10
		FULL = 20
	#



	LOG_LEVEL_TO_COLOR_MAP = {
		EnumLogLevel.TRACE: '\033[90m',
		EnumLogLevel.DEBUG: '\033[90m',
		EnumLogLevel.NOTICE: '\033[90m',
		EnumLogLevel.STDOUT: '\033[97m',
		EnumLogLevel.INFO: '\033[37m',
		EnumLogLevel.WARNING: '\033[93m',
		EnumLogLevel.ERROR: '\033[91m',
		EnumLogLevel.STDERR: '\033[91m',
		EnumLogLevel.EXCEPTION: '\033[91m',
		EnumLogLevel.SUCCESS: '\033[92m',
	}
	#STACKTRACE_COLOR = "\033[38;2;204;102;0m"
	STACKTRACE_COLOR = "\033[93m"
	RESET_COLOR = '\033[0m'



	def __init__(self, bIncludeIDs = False, fillChar = "\t"):
		self.__fillChar = fillChar
		self.__indentBuffer = fillChar
		self.__includeIDs = bIncludeIDs
		self.__outputMode = ColoredLogMessageFormatter.EnumOutputMode.SHORTED
	#



	def setOutputMode(self, outputMode:EnumOutputMode):
		if outputMode is None:
			outputMode = ColoredLogMessageFormatter.EnumOutputMode.SHORTED
		self.__outputMode = outputMode
	#



	#
	# Create and return a string representation of the specified log entry.
	#
	# @param		list logEntryStruct			A log entry structure. See <c>AbstractLogger._logi()</c> for a detailed description.
	# @return		str							Returns the string representation of the log message.
	#
	def format(self, logEntryStruct):
		sID = str(logEntryStruct[1]) if (logEntryStruct != None) else "-"
		indentationLevel = logEntryStruct[2]
		while indentationLevel > len(self.__indentBuffer):
			self.__indentBuffer += self.__fillChar
		sIndent = self.__indentBuffer[0:indentationLevel]
		sParentID = str(logEntryStruct[3]) if (logEntryStruct != None) else "-"
		sTimeStamp = "[" + datetime.datetime.fromtimestamp(logEntryStruct[4]).strftime('%Y-%m-%d %H:%M:%S') + "]"
		sLogType = AbstractLogMessageFormatter.LOG_LEVEL_TO_STR_MAP[logEntryStruct[5]]

		if self.__includeIDs:
			s3 = "(" + sParentID + "|" + sID + ") " + sTimeStamp + " "
		else:
			s3 = sTimeStamp + " "
		s1 = sIndent + ColoredLogMessageFormatter.LOG_LEVEL_TO_COLOR_MAP[logEntryStruct[5]] + s3
		s2 = sIndent + ColoredLogMessageFormatter.STACKTRACE_COLOR + s3

		if logEntryStruct[0] == "txt":
			sLogMsg = logEntryStruct[6]
			return s1 + sLogType + ": " + sLogMsg + ColoredLogMessageFormatter.RESET_COLOR
		elif logEntryStruct[0] == "ex":
			sExClass = logEntryStruct[6]
			sLogMsg = logEntryStruct[7]
			ret = []
			ret.append(s1 + sLogType + ": " + sExClass + ": " + sLogMsg + ColoredLogMessageFormatter.RESET_COLOR)
			if logEntryStruct[8] != None:
				if self.__outputMode == ColoredLogMessageFormatter.EnumOutputMode.FULL:
					for (stPath, stLineNo, stModuleName, stLine) in logEntryStruct[8]:
						ret.append(s2 + "STACKTRACE: " + stPath + ":" + str(stLineNo) + " " + stModuleName + "    # " + stLine + ColoredLogMessageFormatter.RESET_COLOR)
				elif self.__outputMode == ColoredLogMessageFormatter.EnumOutputMode.SHORTED:
					stPath, stLineNo, stModuleName, stLine = logEntryStruct[8][-1]
					ret.append(s2 + "STACKTRACE: " + stPath + ":" + str(stLineNo) + " " + stModuleName + "    # " + stLine + ColoredLogMessageFormatter.RESET_COLOR)
			return ret
		elif logEntryStruct[0] == "desc":
			sLogMsg = logEntryStruct[6]
			return s1 + sLogType + ": " + sLogMsg + ColoredLogMessageFormatter.RESET_COLOR
		else:
			raise Exception()
	#

#





COLOR_LOG_MESSAGE_FORMATTER = ColoredLogMessageFormatter()








