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
# This object represents a roll-over enabled log file on disk log messages can be written to. Data is encoded using utf-8.
#
class RollOverLogFile(object):

	#
	# Constructor method.
	#
	# @param		str filePath				The path of the file to write the log data to. If <c>rollOverMode</c> is not <c>None</c>
	#											you need to use the following shortcuts within the file path to be filled in with date and
	#											time values:
	#											* %Y - year (f.e. 2017)
	#											* %m - month (f.e. 08)
	#											* %d - day (f.e. 02)
	#											* %H - hour (f.e. 03)
	#											* %M - minute (f.e. 49)
	#											* %S - second (f.e. 07)
	#											All values used in the pattern elements are padded with zeros.
	# @param		str rollOverMode			Either specify <c>None</c> if no roll-over should be used. Otherwise
	#											specify either "second", "minute", "hour", "day" or "month".
	# @param		bool bAppendToExistingFile	If <c>True</c> a possibly already existing file will be reused, data will
	#											be appended. If <c>False</c> the file will be recreated if it already exists.
	# @param		bool bFlushAfterEveryWrite	If <c>True</c> perform a flush after every write.
	# @param		int fileMode				If not <c>None</c> <c>chmod()</c> will be called with these file modes specified here.
	#
	def __init__(self, filePath, rollOverMode, bAppendToExistingFile, bFlushAfterEveryWrite, fileMode):
		assert isinstance(filePath, str)
		assert isinstance(bFlushAfterEveryWrite, bool)
		assert isinstance(bAppendToExistingFile, bool)
		if fileMode is not None:
			assert isinstance(fileMode, int)
		if rollOverMode is not None:
			assert isinstance(rollOverMode, str)
			assert rollOverMode in ["second", "minute", "hour", "day", "month", "none"]
			if rollOverMode == "none":
				rollOverMode = None

		self.__fileCreationTimeStamp = datetime.datetime.now()
		self.__rollOverMode = rollOverMode
		self.__filePath = filePath
		self.__bFlushAfterEveryWrite = bFlushAfterEveryWrite
		self.__bAppendToExistingFile = bAppendToExistingFile
		self.__fileMode = fileMode

		realFilePath = self.__buildFilePath(filePath, self.__fileCreationTimeStamp)
		if not bAppendToExistingFile:
			if os.path.isfile(realFilePath):
				os.unlink(realFilePath)
		self.__f = open(realFilePath, "a")
		if fileMode is not None:
			os.chmod(realFilePath, fileMode)

		self.__bIsDirty = False
	#



	def __isRollOverRequired(self, now):
		if self.__rollOverMode is None:
			return False

		if self.__rollOverMode == "second":
			if (now.second != self.__fileCreationTimeStamp.second) or (now.minute != self.__fileCreationTimeStamp.minute) \
				or (now.hour != self.__fileCreationTimeStamp.hour) or (now.day != self.__fileCreationTimeStamp.day) \
				or (now.month != self.__fileCreationTimeStamp.month) or (now.year != self.__fileCreationTimeStamp.year):
				return True
		elif self.__rollOverMode == "minute":
			if (now.minute != self.__fileCreationTimeStamp.minute) \
				or (now.hour != self.__fileCreationTimeStamp.hour) or (now.day != self.__fileCreationTimeStamp.day) \
				or (now.month != self.__fileCreationTimeStamp.month) or (now.year != self.__fileCreationTimeStamp.year):
				return True
		elif self.__rollOverMode == "hour":
			if (now.hour != self.__fileCreationTimeStamp.hour) or (now.day != self.__fileCreationTimeStamp.day) \
				or (now.month != self.__fileCreationTimeStamp.month) or (now.year != self.__fileCreationTimeStamp.year):
				return True
		elif self.__rollOverMode == "day":
			if (now.day != self.__fileCreationTimeStamp.day) \
				or (now.month != self.__fileCreationTimeStamp.month) or (now.year != self.__fileCreationTimeStamp.year):
				return True
		elif self.__rollOverMode == "month":
			if (now.month != self.__fileCreationTimeStamp.month) or (now.year != self.__fileCreationTimeStamp.year):
				return True

		return False
	#



	def __toStr(self, number, size):
		s = str(number)
		while len(s) < size:
			s = "0" + s
		return s
	#



	def __buildFilePath(self, filePath, timestamp):
		dataTriples = (
			("Y", 4, timestamp.year),
			("m", 2, timestamp.month),
			("d", 2, timestamp.day),
			("H", 2, timestamp.hour),
			("M", 2, timestamp.minute),
			("S", 2, timestamp.second)
		)

		ret = ""
		bNextCharIsSymbolic = False
		for c in filePath:
			if bNextCharIsSymbolic:
				bReplaced = False
				for (key, paddingSize, value) in dataTriples:
					if key == c:
						ret += self.__toStr(value, paddingSize)
						bReplaced = True
						break
				if not bReplaced:
					ret += c
				bNextCharIsSymbolic = False
			else:
				if c == '%':
					bNextCharIsSymbolic = True
				else:
					ret += c

		return ret
	#



	#
	# Write one or more text lines to the log file.
	#
	# @param		str prefix				If not <c>None</c> this text is prepended to the log file.
	# @param		mixed lineOrLines		A single text string or a list of text lines to write. Don't specify <c>None</c> here.
	#
	def print(self, prefix, lineOrLines):
		if self.__f.closed:
			raise Exception("File already closed!")

		now = datetime.datetime.now()
		if self.__isRollOverRequired(now):
			self.__f.flush()
			self.__f.close()
			realFilePath = self.__buildFilePath(self.__filePath, now)
			if not self.__bAppendToExistingFile:
				if os.path.isfile(realFilePath):
					os.unlink(realFilePath)
			self.__f = open(realFilePath, "a")
			if self.__fileMode is not None:
				os.chmod(realFilePath, self.__fileMode)
			self.__fileCreationTimeStamp = now

		if isinstance(lineOrLines, str):
			if prefix is None:
				self.__f.write(lineOrLines + "\n")
			else:
				self.__f.write(prefix + lineOrLines + "\n")
		else:
			if prefix is None:
				for line in lineOrLines:
					self.__f.write(line + "\n")
			else:
				for line in lineOrLines:
					self.__f.write(prefix + line + "\n")

		if self.__bFlushAfterEveryWrite:
			self.__f.flush()
			self.__bIsDirty = False
		else:
			self.__bIsDirty = True
	#



	#
	# Close the file.
	#
	def close(self):
		if not self.__f.closed:
			self.__f.flush()
			self.__f.close()
	#



	#
	# Checks if the file is closed.
	#
	# @return	bool		Returns <c>true</c> if the file is already closed.
	#
	@property
	def isClosed(self):
		return self.__f.closed
	#



	#
	# Checks if the file is closed.
	#
	# @return	bool		Returns <c>true</c> if the file is already closed.
	#
	@property
	def closed(self):
		return self.__f.closed
	#



#









