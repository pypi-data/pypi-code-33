#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re

from .IDCounter import IDCounter

from .EnumLogLevel import EnumLogLevel
from .AbstractLogger import AbstractLogger
from .BufferLogger import BufferLogger
from .ConsoleLogger import ConsoleLogger
from .DetectionLogger import DetectionLogger
from .FilterLogger import FilterLogger
from .MulticastLogger import MulticastLogger
from .NamedMulticastLogger import NamedMulticastLogger
from .NullLogger import NullLogger
#from .SimpleFileLogger import SimpleFileLogger
from .FileLogger import FileLogger
from .StringListLogger import StringListLogger

from .AbstractLogMessageFormatter import AbstractLogMessageFormatter
from .LogMessageFormatter import LogMessageFormatter, DEFAULT_LOG_MESSAGE_FORMATTER
from .ColoredLogMessageFormatter import ColoredLogMessageFormatter, COLOR_LOG_MESSAGE_FORMATTER





def instantiateLogMsgFormatter(cfg):
	if isinstance(cfg, dict):
		logMsgFormatterType = cfg["type"]
		if logMsgFormatterType == "default":
			if "extensitivity" in cfg:
				extensitivity = cfg["extensitivity"]
				if extensitivity == "full":
					DEFAULT_LOG_MESSAGE_FORMATTER.setOutputMode(DEFAULT_LOG_MESSAGE_FORMATTER.EnumOutputMode.FULL)
				elif extensitivity in [ "short", "shorted", "shortened" ]:
					DEFAULT_LOG_MESSAGE_FORMATTER.setOutputMode(DEFAULT_LOG_MESSAGE_FORMATTER.EnumOutputMode.SHORTED)
				elif extensitivity == "veryShort":
					DEFAULT_LOG_MESSAGE_FORMATTER.setOutputMode(DEFAULT_LOG_MESSAGE_FORMATTER.EnumOutputMode.VERY_SHORT)
				else:
					raise Exception("Unknown extensitivity: " + repr(extensitivity))
			return DEFAULT_LOG_MESSAGE_FORMATTER
		elif logMsgFormatterType == "color":
			if "extensitivity" in cfg:
				extensitivity = cfg["extensitivity"]
				if extensitivity == "full":
					COLOR_LOG_MESSAGE_FORMATTER.setOutputMode(COLOR_LOG_MESSAGE_FORMATTER.EnumOutputMode.FULL)
				elif extensitivity in [ "short", "shorted", "shortened" ]:
					COLOR_LOG_MESSAGE_FORMATTER.setOutputMode(COLOR_LOG_MESSAGE_FORMATTER.EnumOutputMode.SHORTED)
				elif extensitivity == "veryShort":
					COLOR_LOG_MESSAGE_FORMATTER.setOutputMode(COLOR_LOG_MESSAGE_FORMATTER.EnumOutputMode.VERY_SHORT)
				else:
					raise Exception("Unknown extensitivity: " + repr(extensitivity))
			return COLOR_LOG_MESSAGE_FORMATTER
		else:
			raise Exception("Unknown log message formatter: " + repr(cfg))
	else:
		if cfg == "default":
			return DEFAULT_LOG_MESSAGE_FORMATTER
		elif cfg == "color":
			return COLOR_LOG_MESSAGE_FORMATTER
		else:
			raise Exception("Unknown log message formatter: " + repr(cfg))
#



def instantiate(cfg):
	loggerType = cfg["type"]

	if loggerType == "BufferLogger":
		return BufferLogger.create()

	elif loggerType == "ConsoleLogger":
		logMsgFormatter = None
		if "logMsgFormatter" in cfg:
			logMsgFormatter = instantiateLogMsgFormatter(cfg["logMsgFormatter"])
		return ConsoleLogger.create(logMsgFormatter = logMsgFormatter)

	elif loggerType == "DetectionLogger":
		return DetectionLogger.create(instantiate(cfg["nested"]))

	elif loggerType == "FilterLogger":
		if "minLogLevel" in cfg:
			logLevel = EnumLogLevel.parse(cfg["minLogLevel"])
		else:
			logLevel = EnumLogLevel.WARNING
		return FilterLogger.create(instantiate(cfg["nested"]), minLogLevel = logLevel)

	elif loggerType == "MulticastLogger":
		loggers = []
		for item in cfg["nested"]:
			loggers.append(instantiate(item))
		return MulticastLogger.create(* loggers)

	elif loggerType == "NamedMulticastLogger":
		loggers = {}
		for itemKey in cfg["nested"]:
			loggers[itemKey] = instantiate(cfg["nested"][itemKey])
		return NamedMulticastLogger.create(kwargs = loggers)

	elif loggerType == "NullLogger":
		return NullLogger.create()

	elif loggerType == "FileLogger":
		mode = cfg.get("fileMode", None)
		if mode != None:
			if isinstance(mode, int):
				mode = str(mode)
			if isinstance(mode, str):
				if re.match("^[0-7][0-7][0-7]$", mode):
					mode = int(mode, 8)
				else:
					raise Exception("Invalid mode specified for file logger!")
			else:
				raise Exception("Invalid mode specified for file logger!")
		return FileLogger.create(
			cfg["filePath"],
			cfg.get("rollOver", None),
			cfg.get("bAppendToExistingFile", True),
			cfg.get("bFlushAfterEveryLogMessage", True),
			mode)

	elif loggerType == "StringListLogger":
		return StringListLogger.create()

	else:
		raise Exception("Unknown logger type: " + loggerType)
#










