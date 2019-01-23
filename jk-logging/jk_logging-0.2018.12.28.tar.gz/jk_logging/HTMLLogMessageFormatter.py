#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime

from enum import Enum

from .EnumLogLevel import EnumLogLevel
from .AbstractLogMessageFormatter import AbstractLogMessageFormatter




#
# This is a default formatter for log messages. It produces human readable output for log messages.
#
class HTMLLogMessageFormatter(AbstractLogMessageFormatter):

	class EnumOutputMode(Enum):
		VERY_SHORT = 0
		SHORTED = 10
		FULL = 20
	#



	LOG_LEVEL_TO_COLOR_MAP = {
		EnumLogLevel.TRACE: "#a0a0a0",
		EnumLogLevel.DEBUG: "#a0a0a0",
		EnumLogLevel.NOTICE: "#a0a0a0",
		EnumLogLevel.STDOUT: "#404040",
		EnumLogLevel.INFO: "#404040",
		EnumLogLevel.WARNING: "#804040",
		EnumLogLevel.ERROR: "#800000",
		EnumLogLevel.STDERR: "#800000",
		EnumLogLevel.EXCEPTION: "#800000",
		EnumLogLevel.SUCCESS: "#008000",
	}
	#STACKTRACE_COLOR = "\033[38;2;204;102;0m"
	STACKTRACE_COLOR = "#800000"



	def __init__(self, bIncludeIDs = False, fillChar = "&nbsp;&nbsp;&nbsp;&nbsp;", bLinesWithBRTag = False):
		self.__fillChar = fillChar
		self.__indentBuffer = fillChar
		self.__includeIDs = bIncludeIDs
		self.__outputMode = HTMLLogMessageFormatter.EnumOutputMode.SHORTED
		self.__bLinesWithBRTag = bLinesWithBRTag
	#



	def setOutputMode(self, outputMode:EnumOutputMode):
		if outputMode is None:
			outputMode = HTMLLogMessageFormatter.EnumOutputMode.SHORTED
		self.__outputMode = outputMode
	#



	#
	# Create and return a string representation of the specified log entry.
	#
	# @param		list logEntryStruct			A log entry structure. See <c>AbstractLogger._logi()</c> for a detailed description.
	# @return		str							Returns the string representation of the log message.
	#
	def format(self, logEntryStruct):
		term = "</span>"
		if self.__bLinesWithBRTag:
			term += "</br>"

		sID = str(logEntryStruct[1]) if (logEntryStruct != None) else "-"
		indentationLevel = logEntryStruct[2]
		while indentationLevel > len(self.__indentBuffer):
			self.__indentBuffer += self.__fillChar
		sIndent = self.__indentBuffer[0:indentationLevel*len(self.__fillChar)]
		sParentID = str(logEntryStruct[3]) if (logEntryStruct != None) else "-"
		sTimeStamp = "[" + datetime.datetime.fromtimestamp(logEntryStruct[4]).strftime('%Y-%m-%d %H:%M:%S') + "]"
		sLogType = AbstractLogMessageFormatter.LOG_LEVEL_TO_STR_MAP[logEntryStruct[5]]

		if self.__includeIDs:
			s3 = "(" + sParentID + "|" + sID + ") " + sTimeStamp + " "
		else:
			s3 = sTimeStamp + " "
		s1 = sIndent + "<span style=\"color:" + HTMLLogMessageFormatter.LOG_LEVEL_TO_COLOR_MAP[logEntryStruct[5]] + "\">" + s3
		s2 = sIndent + "<span style=\"color:" + HTMLLogMessageFormatter.STACKTRACE_COLOR + "\">" + s3

		if logEntryStruct[0] == "txt":
			sLogMsg = logEntryStruct[6]
			return s1 + sLogType + ": " + sLogMsg + term
		elif logEntryStruct[0] == "ex":
			sExClass = logEntryStruct[6]
			sLogMsg = logEntryStruct[7]
			ret = []
			ret.append(s1 + sLogType + ": " + sExClass + ": " + sLogMsg + term)
			if logEntryStruct[8] != None:
				if self.__outputMode == HTMLLogMessageFormatter.EnumOutputMode.FULL:
					for (stPath, stLineNo, stModuleName, stLine) in logEntryStruct[8]:
						ret.append(s2 + "STACKTRACE: " + stPath + ":" + str(stLineNo) + " " + stModuleName + "    # " + stLine + term)
				elif self.__outputMode == HTMLLogMessageFormatter.EnumOutputMode.SHORTED:
					stPath, stLineNo, stModuleName, stLine = logEntryStruct[8][-1]
					ret.append(s2 + "STACKTRACE: " + stPath + ":" + str(stLineNo) + " " + stModuleName + "    # " + stLine + term)
			return ret
		elif logEntryStruct[0] == "desc":
			sLogMsg = logEntryStruct[6]
			return s1 + sLogType + ": " + sLogMsg + term
		else:
			raise Exception()
	#

#



HTML_LOG_MESSAGE_FORMATTER = HTMLLogMessageFormatter()







