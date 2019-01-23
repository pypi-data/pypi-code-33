#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from ._inst import instantiateLogMsgFormatter, instantiate




class LoggerInstanceManager(object):

	#
	# Initialization method
	#
	# @param		dict cfgs		The configuration describing how to instantiate the loggers
	#
	def __init__(self, cfgs):
		self.__loggerCfgs = cfgs
		self.__loggerCategoryMaps = {}

		self.__loggerCategories = list(cfgs.keys())
		self.__loggerCategories.sort()
		self.__loggerCategories = tuple(self.__loggerCategories)
	#



	#
	# Returns a list of all categories configured.
	#
	@property
	def categories(self):
		return self.__loggerCategories
	#



	def __getLoggCfg(self, loggerCategory, loggerID):
		cfg = self.__loggerCfgs.get(loggerCategory, None)
		if cfg is None:
			raise Exception("No logger configuration specified for category: " + loggerCategory)

		if loggerID is None:
			if "static" in cfg:
				cfg = cfg["static"]
				sStyle = "static"
			else:
				sStyle = cfg.get("style", None)
				if sStyle is None:
					raise Exception("Missing type for logger configuration in category: " + loggerCategory)
				if sStyle != "static":
					raise Exception("Logger configuration for category '" + loggerCategory + "' is not 'static'!")
		else:
			if "dynamic" in cfg:
				cfg = cfg["dynamic"]
				sStyle = "dynamic"
			else:
				sStyle = cfg.get("style", None)
				if sStyle is None:
					raise Exception("Missing type for logger configuration in category: " + loggerCategory)
				if sStyle != "dynamic":
					raise Exception("Logger configuration for category '" + loggerCategory + "' is not 'dynamic'!")

		cfg = cfg.copy()
		if sStyle == "dynamic":
			adaptationMap = {
				"category": loggerCategory,
				"id": loggerID,
			}
		else:
			adaptationMap = {
				"category": loggerCategory,
			}
		cfg = self.____adaptValue(cfg, adaptationMap)

		return cfg
	#



	def ____adaptValue(self, value, adaptationMap):
		if isinstance(value, str):
			return self.____adaptStr(value, adaptationMap)
		elif isinstance(value, (tuple, list)):
			i = 0
			for v in value:
				value[i] = self.____adaptValue(v, adaptationMap)
				i += 1
		elif isinstance(value, dict):
			for key in value:
				v = value[key]
				value[key] = self.____adaptValue(v, adaptationMap)
		return value
	#



	def ____adaptStr(self, value, adaptationMap):
		assert isinstance(value, str)
		assert value != None

		for key in adaptationMap:
			s = "$(" + key + ")"
			while True:
				pos = value.find(s)
				if pos < 0:
					break
				value = value[0:pos] + adaptationMap[key] + value[pos+len(s):]
		return value
	#



	def getCreateLogger(self, loggerCategory, loggerID = None):
		assert isinstance(loggerCategory, str)

		loggerCategoryEntry = self.__loggerCategoryMaps.get(loggerCategory, None)
		if loggerCategoryEntry is None:
			loggerCategoryEntry = [None, {}]
			self.__loggerCategoryMaps[loggerCategory] = loggerCategoryEntry

		if loggerID is None:
			if loggerCategoryEntry[0] != None:
				return loggerCategoryEntry[0]
			else:
				cfg = self.__getLoggCfg(loggerCategory, loggerID)
				loggerCategoryEntry[0] = instantiate(cfg)
				return loggerCategoryEntry[0]
		else:
			loggerID = str(loggerID)
			logger = loggerCategoryEntry[1].get(loggerID, None)
			if logger != None:
				return logger
			else:
				cfg = self.__getLoggCfg(loggerCategory, loggerID)
				logger = instantiate(cfg)
				loggerCategoryEntry[1][loggerID] = logger
				return logger
	#



	def createLogger(self, loggerCategory, loggerID = None):
		assert isinstance(loggerCategory, str)

		loggerCategoryEntry = self.__loggerCategoryMaps.get(loggerCategory, None)
		if loggerCategoryEntry is None:
			loggerCategoryEntry = [None, {}]
			self.__loggerCategoryMaps[loggerCategory] = loggerCategoryEntry

		if loggerID is None:
			if loggerCategoryEntry[0] != None:
				raise Exception("A logger for category " + str(loggerCategory) + " already exists!")
			else:
				cfg = self.__getLoggCfg(loggerCategory, loggerID)
				loggerCategoryEntry[0] = instantiate(cfg)
				return loggerCategoryEntry[0]
		else:
			loggerID = str(loggerID)
			logger = loggerCategoryEntry[1].get(loggerID, None)
			if logger != None:
				raise Exception("A logger for category " + str(loggerCategory) + " with ID " + loggerID + " already exists!")
			else:
				cfg = self.__getLoggCfg(loggerCategory, loggerID)
				logger = instantiate(cfg)
				loggerCategoryEntry[1][loggerID] = logger
				return logger
	#



	def getLogger(self, loggerCategory, loggerID = None):
		assert isinstance(loggerCategory, str)

		loggerCategoryEntry = self.__loggerCategoryMaps.get(loggerCategory, None)
		if loggerCategoryEntry is None:
			return None

		if loggerID is None:
			return loggerCategoryEntry[0]
		else:
			loggerID = str(loggerID)
			return loggerCategoryEntry[1].get(loggerID, None)
	#



	def closeLogger(self, loggerCategory, loggerID):
		assert isinstance(loggerCategory, str)

		loggerCategoryEntry = self.__loggerCategoryMaps.get(loggerCategory, None)
		if loggerCategoryEntry is None:
			raise Exception("No such log category: " + loggerCategory)

		if loggerID is None:
			if loggerCategoryEntry[0] is None:
				raise Exception("There is no logger for category " + str(loggerCategory) + "!")
			else:
				loggerCategoryEntry[0].close()
				loggerCategoryEntry[0] = None
		else:
			loggerID = str(loggerID)
			logger = loggerCategoryEntry[1].get(loggerID, None)
			if logger != None:
				logger.close()
				loggerCategoryEntry[1][loggerID] = None
			else:
				raise Exception("There is no logger for category " + str(loggerCategory) + " with ID " + loggerID + "!")
	#



	def closeAllLoggers(self):
		for loggereCategory in self.__loggerCategoryMaps:
			loggerCategoryEntry = self.__loggerCategoryMaps[loggereCategory]
			if loggerCategoryEntry[0] != None:
				loggerCategoryEntry[0].close()
				loggerCategoryEntry[0] = None
			for loggerID in loggerCategoryEntry[1]:
				logger = loggerCategoryEntry[1][loggerID]
				logger.close()
			loggerCategoryEntry[1].clear()
	#



#








