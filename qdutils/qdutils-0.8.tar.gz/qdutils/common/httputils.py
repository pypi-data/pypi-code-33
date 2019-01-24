#  -*- coding: utf-8 -*-

'''

@desc: 
@author: tony
@Date: 2018/12/26 下午7:06

'''

import urllib2
import requests
import traceback
import time


class httputils(object):
    MAX_RETRY_NUM = 2
    SLEEP_SECONDS = 3

    '''
    http get请求
    '''

    @staticmethod
    def http_get(url, retry_num=None):
        """
            get 请求
        :param url: 请求url 
        :param retry_num: 重试次数，默认2次
        :return:
            flag:   true：成功，false：失败
            result  返回结果
        """
        has_retry_num = 0
        max_retry_num = 0
        flag = False
        if retry_num is None:
            max_retry_num = httputils.MAX_RETRY_NUM
        else:
            max_retry_num = retry_num
        res = ''
        while not flag and has_retry_num <= max_retry_num:
            try:
                req = urllib2.Request(url)
                res_data = urllib2.urlopen(req)
                res = res_data.read()
                flag = True
                break
            except Exception:
                has_retry_num = has_retry_num + 1
                traceback.print_exc()
                time.sleep(httputils.SLEEP_SECONDS)
        return flag, res

    '''
    http post请求
    @:param
        json_str 请求参数json
    '''

    @staticmethod
    def http_post(url, data_obj=None, json_str=None, retry_num=None, headers={}):
        """
            post 请求
        :param url: 请求url
        :param data_obj: (optional) Dictionary, bytes, or file-like object
        :param json_str: json串 
        :param retry_num: 重试次数，默认2次
        :param headers: 
        :return:
            flag:   true：成功，false：失败
            result  返回结果
        """
        flag = False
        result = ''
        has_retry_num = 0
        max_retry_num = 0
        if retry_num is None:
            max_retry_num = httputils.MAX_RETRY_NUM
        else:
            max_retry_num = retry_num
        while not flag and has_retry_num <= max_retry_num:
            try:
                res = requests.post(url,
                                    data=data_obj, json=json_str, headers=headers)
                if res.status_code == 200:
                    result = res.text
                    flag = True
                    break
                else:
                    has_retry_num = has_retry_num + 1
                    time.sleep(httputils.SLEEP_SECONDS)
            except Exception, e:
                traceback.print_exc()
                has_retry_num = has_retry_num + 1
                time.sleep(httputils.SLEEP_SECONDS)
        return flag, result
