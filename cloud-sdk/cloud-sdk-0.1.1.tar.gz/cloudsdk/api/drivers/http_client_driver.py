# coding=utf-8
"""
    具体操作基类
    @author 潘晓华
    @written at 2017-08-03 10:20am
"""

from abc import abstractmethod


class HttpClientDriver(object):

    # 请求后台
    @abstractmethod
    def request(self, action_data={}, method='GET'):
        pass

    # 解析请求数据
    @abstractmethod
    def parse(self, respons=''):
        pass

