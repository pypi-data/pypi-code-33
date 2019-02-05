#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import os

class ACNLogger:

	def debug(self, message):
		self.logger.debug("["+self.ENV+"]  ["+self.session+"]  ["+self.correlationId+"]  " + message)

	def info(self, message):
		self.logger.info("["+self.ENV+"]  ["+self.session+"]  ["+self.correlationId+"]  " + message)

	def warning(self, message):
		self.logger.warning("["+self.ENV+"]  ["+self.session+"]  ["+self.correlationId+"]  " + message)
			
	def error(self, e):
		self.logger.error("["+self.ENV+"]  ["+self.session+"]  ["+self.correlationId+"]  " + str(e))
			
	def critical(self, e):
		self.logger.critical("["+self.ENV+"]  ["+self.session+"]  ["+self.correlationId+"]  " + str(e))
			
	def exception(self, e):
		if self.ENV != "PRO":
			self.logger.exception("["+self.ENV+"]  ["+self.session+"]  ["+self.correlationId+"]  " + str(e))
		else:
			self.error(e)

	def setSession(self, session):
		self.session = session

	def setCorrelationId(self, correlationId):
		self.correlationId = correlationId
			

	def __init__(self,name,file=None,console_level="debug",logfile_level="debug"):

		file = file or name+".log"
		_logLevelMap = {
			"debug": logging.DEBUG,
			"info": logging.INFO,
			"warning": logging.WARNING,
			"error": logging.ERROR,
			"critical":logging.CRITICAL
		}

		acn_logger=logging.getLogger(name) # Creating the new logger
		acn_logger.setLevel(logging.DEBUG) # Setting new logger level to INFO or above
		acn_logger.propagate = False


		console_handler=logging.StreamHandler()
		console_handler.setLevel(_logLevelMap[console_level])


		file_handler=logging.FileHandler(file)
		file_handler.setLevel(_logLevelMap[logfile_level])


		acn_logger.addHandler(file_handler) #Adding file handler to the new logger
		acn_logger.addHandler(console_handler)

		formatter=logging.Formatter('[%(asctime)s]  [%(levelname)s]  [%(name)s]  %(message)s') #Creating a formatter

		file_handler.setFormatter(formatter) #Setting handler format
		console_handler.setFormatter(formatter)

		self.session = "UNDEFINED"
		self.correlationId = "UNDEFINED"

		self.logger=acn_logger

		try:
			self.ENV = os.environ["ENV"]
		except:
			self.ENV = "ENV NOT SET"
			self.warning("Environment variable ENV not set")

		self.info("STARTING MICROSERVICE")