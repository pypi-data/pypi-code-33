#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime


from .EnumLogLevel import EnumLogLevel
from .AbstractLogMessageFormatter import AbstractLogMessageFormatter






#
# This is a default formatter for log messages. It produces human readable output for log messages.
#
class JSONLogMessageFormatter(AbstractLogMessageFormatter):


	def __init__(self, bIncludeIDs = False, fillChar = "\t"):
		self.__fillChar = fillChar
		self.__indentBuffer = fillChar
		self.__includeIDs = bIncludeIDs



	def format(self, logEntryStruct):
		sID = str(logEntryStruct[1]) if (logEntryStruct != None) else "-"
		indentationLevel = logEntryStruct[2]
		while indentationLevel > len(self.__indentBuffer):
			self.__indentBuffer += self.__fillChar
		sIndent = self.__indentBuffer[0:indentationLevel]
		sParentID = str(logEntryStruct[3]) if (logEntryStruct != None) else "-"
		sTimeStamp = "[" + datetime.datetime.fromtimestamp(logEntryStruct[4]).strftime('%Y-%m-%d %H:%M:%S') + "]"
		sLogType = AbstractLogMessageFormatter.LOG_LEVEL_TO_STR_MAP[logEntryStruct[5]]

		s = sIndent
		if self.__includeIDs:
			s += "(" + sParentID + "|" + sID + ") "
		s += sTimeStamp + " "

		if logEntryStruct[0] == "txt":
			sLogMsg = logEntryStruct[6]
			return s + sLogType + ": " + sLogMsg
		elif logEntryStruct[0] == "ex":
			sExClass = logEntryStruct[6]
			sLogMsg = logEntryStruct[7]
			ret = []
			ret.append(s + " "  + sLogType + ": " + sExClass + ": " + sLogMsg)
			if logEntryStruct[8] != None:
				for (stPath, stLineNo, stModuleName, stLine) in logEntryStruct[8]:
					ret.append(s + "STACKTRACE: " + stPath + ":" + str(stLineNo) + " " + stModuleName + "    # " + stLine)
			return ret
		elif logEntryStruct[0] == "desc":
			sLogMsg = logEntryStruct[6]
			return s + sLogType + ": " + sLogMsg
		else:
			raise Exception()




JSON_LOG_MESSAGE_FORMATTER = JSONLogMessageFormatter()








