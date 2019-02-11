#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sense_core as sd
from .constants import *

def check_db_exist():
	__label__ = MONITOR_DATABASE_LABEL
	try:
		db = sd.config(__label__, 'database', None)
	except Exception as e:
		db = None
	return db