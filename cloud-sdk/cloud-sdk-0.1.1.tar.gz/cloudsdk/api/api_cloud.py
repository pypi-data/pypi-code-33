# coding=utf-8
"""
    Api总入口
    @author 潘晓华
    @written at 2017-08-03 10:00am
"""

from cloudsdk.config import ApiConfig


class ApiCloud(object):
    @staticmethod
    def request(action_data={}, method='GET'):
        http_client_module = __import__(r'cloudsdk.api.drivers.' + ApiConfig.api_drivers + r'.http_client', fromlist=True)
        http_client = getattr(http_client_module, 'HttpClient')
        return http_client.request(action_data, method)
    @staticmethod
    def tesxt():
        print(ApiConfig.api_drivers)
