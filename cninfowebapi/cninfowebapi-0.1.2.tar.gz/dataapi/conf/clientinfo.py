# -*- coding:utf-8 -*-
"""
FileName: clientinfo.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-25
Description: 接收客户端信息配置.
History: /*
 create 2019-01-25
 */
"""
import os
from enum import Enum


class SaveType(Enum):
    CSV = 1       # CSV文件
    EXCEL = 2     # EXCEL文件
    JSON = 3      # JSON格式文件
    HDF5 = 4      # HDF5文件
    DATABASE = 5  # 关系数据库
    NOSQL = 6     # nosql数据库
    CONSOLE = 7   # 直接打印
    NONE = 9      # 啥也没有


CLIENT_CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
# 获取cninfo-data-platform，也就是项目的根路径
CLIENT_ROOT_PATH = CLIENT_CURRENT_PATH[:CLIENT_CURRENT_PATH.find("cninfo-data-platform\\")+len("cninfo-data-platform\\")]

# CLIENT_SAVE_ENGINE = 'mysql://cninfo:cninfo@127.0.0.1/infodb?charset=utf8'
# 默认存储sqllite数据库, 可以改为mysql\oracle\postgresql等
CLIENT_SAVE_ENGINE = 'sqlite:///' + CLIENT_ROOT_PATH + 'data\\apidb.db'
CLIENT_SAVE_FILEPATH = CLIENT_ROOT_PATH + 'data\\'
CLIENT_SAVE_TYPE = SaveType.CSV

SESSION_CONF_FILEPATH = CLIENT_SAVE_FILEPATH + 'conf\\'

USER_CLIENT_ID = '0ddc14c30d7f4cd1b30261263cb376eb'
USER_CLIENT_SECRET = 'e8cb33ca4aad49a4a742794fd892fd91'


if __name__ == '__main__':
    print(CLIENT_SAVE_ENGINE)
