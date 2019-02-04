# -*- coding:utf-8 -*-
"""
FileName: apilog.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-27
Description: 日志记录.
History: /*
 create 2019-01-27
 */
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from dataapi.conf.clientinfo import CLIENT_ROOT_PATH

logger = logging.getLogger('szxapi')
logger.setLevel(level=logging.INFO)
if not os.path.exists(CLIENT_ROOT_PATH + "logs/"):
      os.makedirs(CLIENT_ROOT_PATH + "logs/")
handler = RotatingFileHandler(CLIENT_ROOT_PATH + "logs/szxapi.log", maxBytes=1*1024, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console)