#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
import abc


from .EnumLogLevel import EnumLogLevel






def _getLogLevelStr(logLevel):
	s = str(logLevel)
	pos = s.rfind(".")
	if pos >= 0:
		s = s[pos+1:]
	return s
#



def createLogMsgTypeStrMap(bPrefixWithSpacesToSameLength = False):
	maxLogLevelLength = len("STACKTRACE")
	for logLevel in EnumLogLevel:
		s = _getLogLevelStr(logLevel)
		logLevelLength = len(s)
		if logLevelLength > maxLogLevelLength:
			maxLogLevelLength = logLevelLength

	logLevelToStrDict = {}
	for logLevel in EnumLogLevel:
		s = _getLogLevelStr(logLevel)
		if bPrefixWithSpacesToSameLength:
			while len(s) < maxLogLevelLength:
				s = " " + s
		logLevelToStrDict[logLevel] = s

	return logLevelToStrDict
#







class AbstractLogMessageFormatter(object):

	LOG_LEVEL_TO_STR_MAP = createLogMsgTypeStrMap(True)



	#
	# Create and return a string representation of the specified log entry. Overwrite this method to implement a log message formatter.
	#
	# @param		list logEntryStruct			A log entry structure. See <c>AbstractLogger._logi()</c> for a detailed description.
	# @return		str							Returns the string representation of the log message.
	#
	@abc.abstractmethod
	def format(self, logEntryStruct):
		pass
	#

#




