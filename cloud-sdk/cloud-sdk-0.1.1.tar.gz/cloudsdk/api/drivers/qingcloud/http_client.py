# coding=utf-8
"""
    公共工具包
    公共函数
    @author 潘晓华
    @written at 2017-08-02 17:00am
"""
import requests
from api_request import ApiRequest
from cloudsdk.api.drivers.http_client_driver import HttpClientDriver
import simplejson


class HttpClient(HttpClientDriver):
    # 访问接口
    @classmethod
    def request(cls, action_data={}, method='GET'):
        # type: (object, object) -> object
        domain, params_string = ApiRequest.build_url(action_data)

        # print(domain + '/?'+params_string)
        try:
            if method == 'GET':
                r = requests.request('get', domain + '/?' +params_string, verify=False)
            elif method == 'POST':
                r = requests.request('post', domain + '/?' +params_string, verify=False)
            else:
                raise Exception("请求方式有误")
            return cls.parse(r.content)
        except Exception, e:
            print(e)

    @classmethod
    def parse(cls, response=''):
        data = simplejson.loads(response)
        return data

if __name__ == '__main__':
    data = {'action': 'DescribeInstances', 'zone': 'gd1'}
    print(HttpClient.request(action_data=data))
