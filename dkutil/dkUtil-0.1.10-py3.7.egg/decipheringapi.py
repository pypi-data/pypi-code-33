# coding:utf-8

import sys
from  urllib import request,error
import json

class decipheringapi(object):
    def __init__(self,host):
        self.host = host
    @staticmethod
    def __http_get_res(url, headers={}):
        '''
        http get请求
        :param url:
        :param headers:
        :return:
        '''
        res_data = request.urlopen(url)
        res = res_data.read()
        return res

    def md5decipheringByOts(self,nolist):
        '''
        通过OTS表格存储查询MD5结果
        :param nolist: md5号码 数组，每次最多100个
        :return:解密后的号码数组
        '''
        path = "/md5-no/md5"
        param = "hash=%s" % (",".join(nolist).upper(),)
        url = "%s%s?%s" % (self.host, path, param)
        res =decipheringapi.__http_get_res(url)
        phoneMD5List = []
        try:
            res_json = json.loads(str(res,encoding='utf-8'))
        except:
            print(sys.exc_info())
        else:
            for jsondata in res_json:
                if "code" in jsondata:
                    if jsondata["code"] == 200:
                        phone = jsondata["value"][0]
                        ""
                        if phone.__len__() == 11 or phone.__len__()==13:
                            phoneMD5List.append(jsondata["value"][0])

        return phoneMD5List
