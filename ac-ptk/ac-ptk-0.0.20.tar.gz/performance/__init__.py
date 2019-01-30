# -*- coding: utf-8 -*-
import os
import time

from performance import config
from performance.config import WORK_DIR

VERSION = [0, 0, 20]


DEBUG = config.DEBUG

# dump时间间隔(s)
DUMP_INTERVAL = config.dump_interval

# 表单名称
SHEET_NAME = "memory"

TODAY = time.strftime("%Y-%m-%d")

TIME = time.strftime("%H-%M-%S")

COLORS = ['none', 'red', 'yellow', 'gray', 'blue', 'black', 'pink', '#ff34b3', '#fff8dc']


DB_NAME = WORK_DIR + os.sep + 'ptk.db'
