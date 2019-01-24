# coding=utf-8

import requests
import unittest
import time
import sys
import hashlib
from urllib.parse import urlparse
import socket
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
)


class AnalysisData(object):
    """
    analysis json module
    """

    def __init__(self, ids, env):
        self.data_url = "http://192.168.225.225/testsystem/caseinfo/testjob?id=%s&env=%s" % (ids, env)
        # self.data_url = "http://192.168.225.224/break/jsonmodule/"
        self.session = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', a)
        self.session.mount('https://', a)
        self.method = None
        self.data = None
        self.params = None
        self.json = None
        self.timeout = 5
        self.header = None
        self.url = None
        self.posttype = None
        self.verify = None
        self.response_status = 0

    def __enter__(self):
        try:
            res = requests.get(self.data_url)
            self.res_json = res.json()
            self._set_url()
            self._set_params()
            self._add_host_ip()
            self._get_response_status()
            return self.req_session(), self.res_json, self._get_response_key_and_value()
        except Exception as e:
            return None, self.res_json, None

    def _set_params(self):
        self.method = self._get_method()
        if self.method == "GET":
            self.params = self._get_params()
        elif self.method == "POST":
            self.posttype = self._get_posttype()
            if self.posttype == "JSON":
                self.json = self._get_params()
            else:
                self.data = self._get_params()

    def _get_method(self):
        """
        get req method
        :return: method get post
        """
        method = self.res_json.get("requestdata").get("method")
        method = str.upper(method)
        return method

    def _get_posttype(self):
        posttype = self.res_json.get("requestdata").get("posttype")
        posttype = str.upper(posttype)
        return posttype

    def _set_url(self):
        url = self.res_json.get("requestdata").get("url")
        self.url = url

    def _get_params(self):
        """
        get params if encryption then encryp
        :return:
        """
        encryption = self.res_json.get("requestdata").get("encryption")
        params = self.res_json.get("requestdata").get("param")
        if encryption:
            for ev in encryption:
                if isinstance(ev, dict) and ev:
                    if str.upper(ev.get("type") if ev.get("type") else "") == "SIGN":
                        appkey = ev.get("appkey")
                        params_add_sign = GenSignData(appkey).get_params_sign(params)
                        return params_add_sign
                    elif str.upper(ev.get("type") if ev.get("type") else "") == "AUTH":
                        # todo encryption
                        en_query = ""
                        return en_query
                    else:
                        return params
                else:
                    return params
        else:
            return params

    def _add_host_ip(self):
        req_head_ip = self.res_json.get("requestdata").get("ip")
        if req_head_ip:
            u = urlparse(self.url)
            domain = u.netloc
            u = u._replace(netloc=req_head_ip)
            self.header = {
                "Host": domain
            }
            self.url = u.geturl()
            self.verify = False

    def req_session(self):
        """
        get a request session, used to get response stuff
        :return: a request session
        """
        self.session = self.session.request(
            method=self.method,
            headers=self.header,
            params=self.params,
            data=self.data,
            json=self.json,
            url=self.url,
            timeout=self.timeout,
            verify=self.verify
        )
        return self.session

    def _get_response_status(self):
        response_status = self.res_json.get("returncheck").get("status")
        self.response_status = response_status

    def _get_response_key_and_value(self):
        backparams = self.res_json.get("returncheck").get("backparam")
        return backparams

    def __exit__(self, exc_type, exc_val, exc_tb):
        # pass
        self.session.close()
        # return None, self.res_json, None


class InterFaceBaseTest(unittest.TestCase):
    """
    base test class
    """

    @classmethod
    def setUpClass(cls, ids, env):
        """
        get parameter and create request session
        :return:
        """
        if len(env) < 2:
            print("missing positional argument")
            sys.exit(1)
        try:
            with AnalysisData(ids, env) as Ad:
                cls.session, cls.res_json, cls.backparams = Ad
                if "application/json" in str.lower(cls.session.headers.get("Content-Type")):
                    cls.res_module = GenResponseModule().get_json_result_keys_and_value_type(cls.session.json())
        except requests.exceptions.ConnectionError as e:
            print(e)
            assert False

    # def setUp(self):
    #     pass

    def test_http_code(self):
        """
        test http code
        :return:
        """
        self.assertEqual(
            self.session.status_code,
            200,
            "HTTP CODE不为200，判定失败！"
        )

    def test_req_elapsed(self):
        """
        test request time spend
        :return:
        """
        self.assertLessEqual(
            self.session.elapsed.total_seconds(),
            1,
            "请求时长超过1000ms，请关注，如频繁出现，建议做压力测试！"
        )

    def test_response_module(self):
        """
        test the response & module type is match
        验证规则：
        假设：A为平台接口返回的json module， B为用例response解析出的json module
        若A中节点must为true，则需要验证B中节点的path、value、type的值是否与A中相等，相等则通过，不等则未通过；
        若A节点must为false，则如果A中节点path匹配到B中节点path，则验证path对应的type是否相等，相等则通过，不等则不通过；
        如果A中节点path未匹配到B中path，则不验证；
        https://stackoverflow.com/questions/19031953/skip-unittest-test-without-decorator-syntax
        :return:
        """
        htype = self.session.headers.get("Content-Type")
        htype = str.lower(htype)
        if "application/json" not in htype:
            raise unittest.case.SkipTest("返回格式不为JSON，跳过！")
        for x in self.backparams:
            if x.get("must"):
                # 验证key存在
                self.assertIn(
                    x.get("path"),
                    self.res_module.keys(),
                    "字段must为True，key值：%s 不存在！" % x.get("path")
                )
                # 验证key类型正确
                if x.get("type") is not None:
                    self.assertEqual(
                        x.get("type"),
                        self.res_module.get(x.get("path")).get("type"),
                        "字段must为True，type类型：%s 不正确！" % str(x.get("type"))
                    )
                # 如果有值，则值要一致
                if x.get("value"):
                    self.assertEqual(
                        x.get("value"),
                        self.res_module.get(x.get("path")).get("value"),
                        "字段must为True，有value的情况下，value值%s不正确" % str(x.get("value"))
                    )
            else:
                # 如果有对应的key，则key对应的类型要一致
                if x.get("path") in self.res_module.keys() and x.get("type") is not None:
                    self.assertEqual(
                        x.get("type"),
                        self.res_module.get(x.get("path")).get("type"),
                        "字段must为False，key值对应类型%s与原类型%s不一致。" % (
                            str(x.get("type")),
                            str(self.res_module.get(x.get("path")).get("type"))
                        )
                    )

    # def tearDown(self):
    #     pass

    # @classmethod
    # def tearDownClass(cls):
    #     """
    #     recycing request session and clean everything
    #     :return:
    #     """
    #     pass


class BaseRunSuite(object):
    """
    suite testcase base class
    """

    def __init__(self, case):
        self.case = case

    def __enter__(self):
        self.result, self.start_time, self.timeToken = self.run()

    def run(self):
        suite = unittest.TestSuite()
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(self.case))
        runner = unittest.TextTestRunner(verbosity=2)
        startTime = time.time()
        result = runner.run(suite)
        stopTime = time.time()
        time_token = "%.3f" % (stopTime - startTime)
        return result, startTime, time_token

    def up_result(self):
        if self.result.testsRun == 0:
            result_status = "请求异常"
        elif self.result.wasSuccessful():
            result_status = "成功"
        elif len(self.result.failures):
            result_status = "用例失败"
        elif len(self.result.errors):
            result_status = "代码错误"
        else:
            result_status = "未知错误"
        interface_name = self.case.__doc__ and self.case.__doc__.split("\n")[1].strip() or ""
        case_name = self.case.__name__
        try:
            case_url = self.case.session.url
            logging.info("用例URL：%s" % case_url)
        except:
            logging.error("用例URL未获取到")
            case_url = None
        try:
            content = self.case.session.content
        except:
            logging.error("用例response未获取到")
            content = None
        try:
            http_status = self.case.session.status_code
            logging.info("请求状态码：%s" % http_status)
        except:
            logging.error("用例的状态码未获取到")
            http_status = None
        try:
            callback_url = self.case.res_json.get("callbackurl")
            logging.info("回调URL：%s" % callback_url)
        except:
            logging.error("回调URL未获取到")
            callback_url = None
        try:
            u = urlparse(case_url)
            domain_ip = socket.getaddrinfo(u.netloc, u.scheme)[0][4][0]
        except:
            domain_ip = None
        log = self.result.separator1 + "\n"
        for x in self.result.errors:
            log = log + x[1] + self.result.separator2 + "\n"
        for y in self.result.failures:
            log = log + y[1] + self.result.separator2 + "\n"
        log += self.result.separator1 + "\n"
        log += json.dumps(self.case.res_json, indent=4)
        report = {
            "interface_name": interface_name,
            "case_name": case_name,
            "case_url": case_url,
            "req_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time)),
            "time_token": self.timeToken,
            "http_status": http_status,
            "head_ip": domain_ip,
            "result_status": result_status,
            "content": content,
            "log": log
        }
        try:
            requests.post(callback_url, data=report, timeout=10)
            logging.info("回调成功")
        except Exception as e:
            logging.error("回调URL请求失败，原因: \n%s" % e)
        return report

    def __exit__(self, exc_type, exc_val, exc_tb):
        # callback data
        self.up_result()
        logging.info("timeToken: %s" % self.timeToken)


class GenResponseModule(object):
    """
    analysis response data module
    """

    def __init__(self):
        self.res_keys_value_type = dict()

    def get_json_result_keys_and_value_type(self, json_dict, key=""):
        """
        将json数据中的key按级别取出，字典级别用/连接，数组级别用[]连接，并排重
        并保存该key值对应的value的类型
        例如：{'code': 'int', 'message': 'str', 'result': 'dict', 'result.has_next': 'bool', 'result.list': 'list', 'result.list-apkname': 'str'}
        :param json_dict: 目标json数据，必须是dict类型
        :param key: 初始值，不用传
        :return: 返回要对比的排重后的数组
        """
        if isinstance(json_dict, list):
            for element in json_dict:
                self.get_json_result_keys_and_value_type(element, key + "[]")
        elif isinstance(json_dict, dict):
            for x in json_dict.keys():
                temp_key = key == "" and x or key + "/" + x
                value_type = not isinstance(json_dict[x], (list, dict)) and {
                    "type": self._change_type_name(json_dict[x]), "value": json_dict[x]} or {
                                 "type": self._change_type_name(json_dict[x])}
                self.res_keys_value_type[str(temp_key)] = value_type
                self.get_json_result_keys_and_value_type(json_dict[x], temp_key)
        return self.res_keys_value_type

    def _change_type_name(self, data):
        if isinstance(data, str):
            return "string"
        if isinstance(data, dict):
            return "object"
        if isinstance(data, list):
            return "array"
        if isinstance(data, bool):
            return "bool"
        if isinstance(data, int):
            return "int"
        if isinstance(data, float):
            return "float"


class GenSignData(object):
    """
    params encryp class
    """

    def __init__(self, appkey):
        # carhelper "@7U$aPOE@$"
        self.appkey = appkey

    def get_params_sign(self, q):
        """
        get _sign param
        :param q: not encryp params
        :return: add _sign params
        """
        if isinstance(q, dict):
            sort_q = sorted(q.items())
            join_q = ""
            for x, y in sort_q:
                if x == "_sign":
                    pass
                else:
                    join_q = join_q + str(x) + str(y)
            join_q = self.appkey + join_q + self.appkey
            m2 = hashlib.md5()
            m2.update(join_q.encode("utf-8"))
            sign_d = str(m2.hexdigest())
            _sign = sign_d.upper()
            q["_sign"] = _sign
            return q
