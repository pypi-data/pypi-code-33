# -*- coding:utf-8 -*-

from SCLibrary.zk import ZookeeperRegistry
from robot.libraries.BuiltIn import BuiltIn
from SCLibrary.fork_requests import RequestsKeywords
from SCLibrary.base import keyword
from json import dumps
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequesterKeywords(RequestsKeywords):

    def __init__(self):
        super(RequesterKeywords, self).__init__()
        self.response = None
        self.zk = None

    @keyword("HTTP Create Session")
    def http_create_session(self, alias, url, headers={}, cookies={},
                            auth=None, timeout=None, proxies=None,
                            verify=False, debug=0, max_retries=3, backoff_factor=0.10, disable_warnings=0):
        """ 创建一个Http的Session：

        ``url`` 域名

        ``alias`` Session的名字

        ``headers`` Headers

        ``cookies`` Cookies

        ``auth`` List of username & password for HTTP Basic Auth

        ``timeout`` Connection timeout

        ``proxies`` Dictionary that contains proxy urls for HTTP and HTTPS communication

        ``max_retries`` 最大重试次数，默认3次

        ``backoff_factor`` 重试间隔时间，默认0.1秒
        """
        if not 'Content-Type' in headers:
            headers['Content-Type'] = 'application/json'
        if not 'charset' in headers:
            headers['charset'] = 'utf-8'
        if not 'Accept-Encoding' in headers:
            headers['Accept-Encoding'] = 'gzip'
        if not 'Accept-Language' in headers:
            headers['Accept-Language'] = 'zh-CN'
        try:
            sc_token = BuiltIn().get_variable_value("${SC_TOKEN}")
            if not 'TT' in headers:
                headers['TT'] = sc_token
            if not 'souche-inc-security-token' in headers:
                headers['souche-inc-security-token'] = sc_token
            if not '_security_token_inc' in headers:
                headers['_security_token_inc'] = sc_token
            if not 'token' in headers:
                headers['token'] = sc_token
            if not '_security_token' in headers:
                headers['_security_token'] = sc_token
            if not 'souche-security-token' in headers:
                headers['souche-security-token'] = sc_token
        except:
            print('警告！ 没有找到全局变量：SC_TOKEN')
            pass
        return super(RequesterKeywords, self).create_session(alias,
                                                             url,
                                                             headers,
                                                             cookies,
                                                             auth,
                                                             timeout,
                                                             proxies,
                                                             verify,
                                                             debug,
                                                             max_retries,
                                                             backoff_factor,
                                                             disable_warnings)

    @keyword("HTTP Post")
    def http_post(self,
                  alias,
                  uri,
                  params=None,
                  headers=None,
                  data=None,
                  json=None,
                  files=None,
                  allow_redirects=None,
                  timeout=None):
        """ 通过Session Alias发起一个Post请求

        ``alias`` 指定Session

        ``uri`` 类似 /api/v1/xxx.json 的部分

        ``params`` 参数，拼接在URL上

        ``data``  参数

        ``headers`` Headers

        ``timeout`` connection timeout
        """
        return self.http_post_request(alias,
                                      uri,
                                      params,
                                      headers,
                                      data,
                                      json,
                                      files,
                                      allow_redirects,
                                      timeout)

    # @keyword("HTTP Post Request")
    def http_post_request(self,
                          alias,
                          uri,
                          params=None,
                          headers=None,
                          data=None,
                          json=None,
                          files=None,
                          allow_redirects=None,
                          timeout=None):
        self.response = None
        self.response = super(RequesterKeywords, self).post_request(alias,
                                                                    uri,
                                                                    data,
                                                                    json,
                                                                    params,
                                                                    headers,
                                                                    files,
                                                                    allow_redirects,
                                                                    timeout)
        return self.response.json()

    @keyword("HTTP Delete")
    def http_delete_request(self,
                            alias,
                            uri,
                            params=None,
                            headers=None,
                            data=None,
                            json=None,
                            allow_redirects=None,
                            timeout=None):
        """ 通过Session Alias发起一个Delete请求

        入参参考 HTTP Post
        """
        self.response = None
        self.response = super(RequesterKeywords, self).delete_request(alias=alias,
                                                                      uri=uri,
                                                                      data=data,
                                                                      json=json,
                                                                      params=params,
                                                                      headers=headers,
                                                                      allow_redirects=allow_redirects,
                                                                      timeout=timeout)
        return self.response.json()

    @keyword("HTTP Put")
    def http_put_request(self,
                         alias,
                         uri,
                         params=None,
                         headers=None,
                         data=None,
                         json=None,
                         files=None,
                         allow_redirects=None,
                         timeout=None):
        """ 通过Session Alias发起一个Put请求

        入参参考 HTTP Post
        """
        self.response = None
        self.response = super(RequesterKeywords, self).put_request(alias=alias,
                                                                   uri=uri,
                                                                   data=data,
                                                                   json=json,
                                                                   params=params,
                                                                   headers=headers,
                                                                   files=files,
                                                                   allow_redirects=allow_redirects,
                                                                   timeout=timeout)
        return self.response.json()

    @keyword("HTTP Get")
    def http_get(self,
                 alias,
                 uri,
                 params=None,
                 headers=None,
                 json=None,
                 allow_redirects=None,
                 timeout=None):
        """ 通过Session Alias发起一个Get请求

        ``alias`` 指定Session

        ``uri`` 类似 /api/v1/xxx.json 的部分

        ``params`` 参数

        ``headers`` Headers

        ``timeout`` connection timeout
        """
        return self.http_get_request(alias,
                                     uri,
                                     params,
                                     headers,
                                     json,
                                     allow_redirects,
                                     timeout)

    # @keyword("HTTP Get Request")
    def http_get_request(self,
                         alias,
                         uri,
                         params=None,
                         headers=None,
                         json=None,
                         allow_redirects=None,
                         timeout=None):
        self.response = None
        self.response = super(RequesterKeywords, self).get_request(alias,
                                                                   uri,
                                                                   headers,
                                                                   json,
                                                                   params,
                                                                   allow_redirects,
                                                                   timeout)
        return self.response.json()

    @keyword("HTTP Delete All Sessions")
    def http_delete_all_session(self):
        """ 清除所有的Session """
        super(RequesterKeywords, self).delete_all_sessions()

    @keyword("HTTP Update Session")
    def http_update_session(self, alias, headers=None, cookies=None):
        """ 更新Session 
        ``alias`` Session名字

        ``headers`` Headers

        ``cookies`` Cookies
        """
        super(RequesterKeywords, self).update_session(alias, headers, cookies)

    @keyword("HTTP Code Should Be")
    def http_code_should_be(self, code):
        """ 断言Code的值，这个code指{success: , code: , data: } 这个返回体的code
        ``code`` 大搜车状态码
        """
        resp_code = self.get_response_value(
            'code', '该关键词 仅适用于类似 {code: xxx} 返回结构')
        if(resp_code != code):
            raise AssertionError("%s != %s" % (code, resp_code))

    @keyword("HTTP Check if Success")
    def http_check_if_success(self):
        """ 断言请求是否成功，依据{success: , code: , data: } 这个返回体的success值
        """
        success = self.get_response_value(
            'success', '该关键词 仅适用于类似 {success: boolean} 返回结构')
        if(success == False):
            raise AssertionError("期望请求成功，但是现在是失败!")

    @keyword("HTTP Check if Failure")
    def http_check_if_failure(self):
        """ 断言请求是否失败，依据{success: , code: , data: } 这个返回体的success值
        """
        success = self.get_response_value(
            'success', '该关键词 仅适用于类似 {success: boolean} 返回结构')
        if(success == True):
            raise AssertionError("期望请求失败，但是现在是成功!")

    @keyword("DUBBO Request")
    def dubbo_post(self, interface, method, token='souche_http_token', type='form', params=None, headers=None):
        """ Dubbo请求
        ``interface`` 微服务接口名

        ``method``   方法名

        ``token``    token，默认souche_http_token

        ``type``     请求头的Content-Type，可选值：form, json， 默认form (application/x-www-form-urlencoded)

        ``params``   参数

        ``headers``  额外需要添加的Headers
        """
        if self.zk is None:
            built_in = BuiltIn()
            rf_zk = built_in.get_variable_value("${RF_ZK}")
            self.zk = ZookeeperRegistry(rf_zk)

        url = self.zk.subscribe(interface)[0]

        session_headers = {}
        if type == 'form':
            # type=json时， Content-Type默认为application/json
            session_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        self.http_create_session(
            alias='dubbo', url='http://%s' % url, headers=session_headers)
        headers = {'_method_name': method, '_dubbo_token': token}
        return self.http_post(alias='dubbo', uri='/%s' % interface, data=params, headers=headers)

    @keyword("DB Mongo Query")
    def db_mongo_query(self, host, name, query, headers=None, page_size=1):
        """ 从Mongo开放的Http api上搜索内容， 不需要DB Connect
        ``host`` Mongo服务的Host

        ``name`` 表名

        ``query`` 查询语句，类似 {_id:"${car_id}"}
        
        ``page_size`` 分页， 默认1
        """
        if headers is None:
            headers = {}
        if not 'X-Requested-With' in headers:
            headers['X-Requested-With'] = 'XMLHttpRequest'
        self.http_create_session(alias='mongo', url=host, headers=headers)
        params = {'query': query, 'collectionName': name,
                  'pageSize': page_size}
        return self.http_post(alias='mongo', uri='/manage/dataManage/findPage.json', params=params, headers=headers)

    @keyword("String To Json")
    def http_to_json(self, content, pretty_print=False):
        """ 字符串转成Json对象， Json对象可以使用${json['xx'][0]}语法
        ``content`` 字符串内容
        """
        return super(RequesterKeywords, self).to_json(alias, headers, cookies)

    @keyword("To String")
    def http_to_string(self, list_or_dict):
        """ 字典、数组转成Json字符串
        ``list_or_dict`` 数组或字典
        """
        return dumps(list_or_dict, ensure_ascii=False)

    def get_response_value(self, key, exception):
        json = self.response.json()
        if(not key in json):
            raise AssertionError(exception)
        return json[key]
