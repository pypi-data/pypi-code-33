# -*- coding:utf-8 -*-
"""
FileName: auth.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-24
Description: 用户授权相关功能，包括获取和刷新token.
History: /*
 create 2019-01-24
 */
"""
__authors__ = ['"apidata" <apidata@cninfo.com.cn>', '"ruitian.chen" <chenruitian@cninfo.com.cn>']

import os
import simplejson as json
import requests
from dataapi.conf.serverinfo import API_SERVER_URL, API_TOKEN_PATH
from dataapi.conf.clientinfo import USER_CLIENT_ID, USER_CLIENT_SECRET, SESSION_CONF_FILEPATH
from dataapi.conf.requestparam import API_REQ_TIMEOUT
from util.datehelper import getlatesttimestr, gettimedif


def savetoken(tokendict):
    """保存最新获取的token 到文件"""
    if not os.path.exists(SESSION_CONF_FILEPATH):
        os.makedirs(SESSION_CONF_FILEPATH, exist_ok=True)
    fw = open(SESSION_CONF_FILEPATH + 'access_token.json', 'w', encoding='utf-8')
    tokendict['savetime'] = getlatesttimestr()
    json.dump(tokendict, fw, ensure_ascii=False, indent=4)
    print('Save access_token to file.')


def readtoken():
    """从文件获取最新的token """
    if os.path.exists(SESSION_CONF_FILEPATH + 'access_token.json'):
        filetoken = open(SESSION_CONF_FILEPATH + 'access_token.json', encoding='utf-8')  # 打开文件
        res = filetoken.read()  # 读文件
        tokendict = json.loads(res)
        tokentime = tokendict["savetime"]
        effectivesecond = tokendict["expires_in"]
        dif = gettimedif(tokentime, getlatesttimestr())
        if dif >= effectivesecond:
            return None
        print('Read access_token from file, get latest token is :' + tokendict["access_token"])
        return tokendict["access_token"]
    else:
        return None


def gettoken():
    """获取token:优先从本地文件获取access_token，获取不到再从服务器请求新的token"""
    token = readtoken()
    if token:
        return token
    tokenurl = API_SERVER_URL + API_TOKEN_PATH
    req_params = {
        'grant_type': 'client_credentials',
        'client_id': USER_CLIENT_ID,
        'client_secret': USER_CLIENT_SECRET
    }
    res = requests.post(tokenurl, data=req_params, timeout=API_REQ_TIMEOUT)
    result = json.loads(res.text)
    if 'error' in result:
        raise Exception(result['error_description'])
    token = result["access_token"]
    savetoken(result)
    return token


if __name__ == '__main__':
    print(gettoken())
