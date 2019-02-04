# -*- coding:utf-8 -*-
"""
FileName: apimap.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-25
Description: API元数据信息.
History: /*
 create 2019-01-25
 */
"""
import os
import simplejson as json
import requests
from dataapi.conf.serverinfo import API_SERVER_URL, API_INFO_PATH
from dataapi.conf.clientinfo import SESSION_CONF_FILEPATH
from dataapi.conf.requestparam import API_REQ_TIMEOUT
from util.auth import gettoken


class APIInfo:

    __apiinfo_dict = {}

    def __init__(self):
        if not self.readapiinfo():
            self.loadapiinfo()

    def loadapiinfo(self):
        apiurl = API_SERVER_URL + API_INFO_PATH
        token = gettoken()
        req_params = {
            'access_token': token
        }
        res = requests.post(apiurl, data=req_params, timeout=API_REQ_TIMEOUT)
        result = json.loads(res.text)
        if result['resultcode'] != 200:
            raise Exception(result['resultmsg'])
        apiinfo = result["records"]
        for api in apiinfo:
            self.__apiinfo_dict[api["name"]] = api
        self.saveapiinfo()
        print('Read apiinfo from server:' + str(len(self.__apiinfo_dict)))

    def saveapiinfo(self):
        if not os.path.exists(SESSION_CONF_FILEPATH):
            os.makedirs(SESSION_CONF_FILEPATH, exist_ok=True)
        fw = open(SESSION_CONF_FILEPATH + 'apiinfo.json', 'w', encoding='utf-8')
        json.dump(self.__apiinfo_dict, fw, ensure_ascii=False, indent=4)

    def readapiinfo(self):
        if os.path.exists(SESSION_CONF_FILEPATH + 'apiinfo.json'):
            fileapiinfo = open(SESSION_CONF_FILEPATH + 'apiinfo.json', encoding='utf-8')  # 打开文件
            res = fileapiinfo.read()  # 读文件
            self.__apiinfo_dict = json.loads(res)
            print('Read apiinfo from file:' + str(len(self.__apiinfo_dict)))
            return True
        else:
            return False

    def getapiinfo(self, apiname):
        apiinfo = None
        if not self.__apiinfo_dict:
            self.loadapiinfo()
        if apiname in self.__apiinfo_dict:
            apiinfo = self.__apiinfo_dict[apiname]
        return apiinfo

    def getapiurl(self, apiname):
        apiinfo = self.getapiinfo(apiname)
        if not apiinfo:
            return None
        apiurl = API_SERVER_URL + '/api/' + apiinfo["prefix_name"] + '/' + apiinfo["url"]
        return apiurl

    def getapilist(self):
        return self.__apiinfo_dict.keys()


if __name__ == '__main__':
    apiinfo = APIInfo()
    print(apiinfo.getapiinfo('p_info3015'))
