# -*- coding:utf-8 -*-
"""
FileName: auth.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-24
Description: 数据接口客户端.
History: /*
 create 2019-01-24
 */
"""
import pandas as pd
import simplejson as json
import requests
import logging
import time
from dataapi.conf.requestparam import API_REQ_TIMEOUT, API_RETRY_TIMES, API_REQ_PAUSE
from dataapi.conf.vars import ERROR_MSG_API_NETWORK
from dataapi.meta.apiinfo import APIInfo
from dataapi.statistics.apistatistics import apistat
from dataapi.conf.apilog import logger
from util.auth import gettoken

logger = logging.getLogger("szxapi." + __name__)


class DataPlatformApiClient:
    """
    数据服务平台请求类，获取API数据的入口。
    用户可以通过该类的 getdata(apiname, paramsdict) 方法获取api数据，只需要提供api名称和必要的参数字典即可。
    对于获取到的数据自动完成存储。
    """
    __apiinfo = None

    def __init__(self):
        self.__apiinfo = APIInfo()
        self.__token = gettoken()

    def listallapis(self):
        """列出所有的API"""
        print(self.__apiinfo.getapilist())

    def apiinfo(self):
        """获取APIInfo实例"""
        if not self.__apiinfo:
            self.__apiinfo = APIInfo()
        return self.__apiinfo

    def getapiurl(self, api_name):
        """获取API相对路径"""
        apiurl = self.apiinfo().getapiurl(api_name)
        return apiurl

    def getapifullurl(self, api_name, paramsdict={}):
        """获取API请求完整URL"""
        apiurl = self.apiinfo().getapiurl(api_name) + '?access_token=' + self.__token
        paramstr = ''
        for (key, value) in paramsdict.items():
            pstr = '&' + key + '=' + value
            paramstr = paramstr + pstr
        apiurl = apiurl + paramstr
        return apiurl

    def getapiname(self, api_name):
        """获取API名称"""
        return self.apiinfo().getapiinfo(api_name)['alias']

    def getapidesc(self, api_name):
        """获取API描述信息"""
        return self.apiinfo().getapiinfo(api_name)['output_describes']

    def getapiparaminfo(self, api_name):
        """获取API输入参数信息"""
        return self.apiinfo().getapiinfo(api_name)['input_parameter']

    def getapicolinfo(self, api_name):
        """获取API输出参数信息"""
        return self.apiinfo().getapiinfo(api_name)['output_parameter']

    def reqapi(self, api_name, params={}, fields=''):
        """API请求发送"""
        for i in range(API_RETRY_TIMES):
            time.sleep(API_REQ_PAUSE*i)
            try:
                apiurl = self.getapiurl(api_name)
                # apiurl = self.getapiurl(api_name) + '?access_token=' + self.__token
                req_params = {
                    'access_token': self.__token
                }
                req_params.update(params)
                logger.info('Start request api ' + api_name)
                logger.info(req_params)
                res = requests.post(apiurl, data=req_params, timeout=API_REQ_TIMEOUT)
                result = json.loads(res.text)
                # 出现 token 失效，取得新token后重新获取数据
                if result['resultcode'] in (404, 405):
                    self.__token = gettoken()
                    res = requests.post(apiurl, data=req_params, timeout=API_REQ_TIMEOUT)
                    result = json.loads(res.text)
                if result['resultcode'] != 200:
                    logger.error(api_name + ' ' + result['resultmsg'])
                    raise Exception(result['resultmsg'])
                # 增加API访问统计
                apistat.visitapi(api_name)
                data = result['records']
                rowcount = result['count']
                logger.info('Get response rowcount: ' + str(rowcount))
                return pd.DataFrame(data)
            except Exception as e:
                logger.warning(api_name + ' ' + str(e))
        raise IOError(ERROR_MSG_API_NETWORK)


"""直接import该对象直接使用，无需实例化"""
apiclient = DataPlatformApiClient()


if __name__ == '__main__':
    # apiclient.listallapis()
    # df = apiclient.reqapi('p_public0006')
    df = apiclient.reqapi('p_public0001', params={'sdate': '20190101', 'edate': '20190115'})
    print(df)
