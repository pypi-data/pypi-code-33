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
from dataapi.conf.webapiconf import SaveType
from dataapi.conf.webapiconf import webapiconf
from dataapi.conf.webapiconf import CLIENT_ROOT_PATH, SESSION_CONF_FILEPATH


# 项目的根路径
CLIENT_ROOT_PATH = CLIENT_ROOT_PATH

CLIENT_SAVE_ENGINE = webapiconf.getclientconf('CLIENT_SAVE_ENGINE')
CLIENT_SAVE_FILEPATH = webapiconf.getclientconf('CLIENT_SAVE_FILEPATH')
CLIENT_SAVE_TYPE = SaveType.CSV

SESSION_CONF_FILEPATH = SESSION_CONF_FILEPATH

USER_CLIENT_ID = webapiconf.getclientconf('USER_CLIENT_ID')
USER_CLIENT_SECRET = webapiconf.getclientconf('USER_CLIENT_SECRET')


if __name__ == '__main__':
    print(CLIENT_SAVE_ENGINE)
