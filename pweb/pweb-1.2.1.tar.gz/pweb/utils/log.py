#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
import logging
from pweb.conf import settings

loggername = path.split(settings.HERE)[-1]

if settings.DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")

logger = logging.getLogger(loggername)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()  # 日志打印到屏幕上
ch.setLevel(level)  # 指定ch日志打印级别
ch.setFormatter(formatter)

logger.addHandler(ch)
