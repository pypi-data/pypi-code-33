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
# This logger just consumes all loggin output without doing anyting with it.
#
class NullLogger(AbstractLogger):


	def __init__(self, idCounter = None):
		super().__init__(idCounter)
	#



	@staticmethod
	def create():
		return _INSTANCE
	#



	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		pass
	#



	def _descend(self, logEntryStruct):
		return self
	#



#



_INSTANCE = NullLogger()













