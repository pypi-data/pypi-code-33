# coding: utf8
# Author:xuyang.li
# EnOS API default client
import logging
import logging.config
import os

from enosapi.request.EnOSRequest import EnOSRequest
from enosapi.util.Sign import Sign
from enosapi.util.const import Const
import urllib2
import json
import time
from poster.streaminghttp import register_openers


class EnOSDefaultClient:
    __logging = logging.getLogger(__name__)

    def __init__(self, url, access_key, secret_key, timeout=30000):
        assert url is not None
        assert access_key is not None
        assert secret_key is not None

        self.url = url
        self.access_key = access_key
        self.secret_key = secret_key
        self.timeout = timeout

        self.setupFileLogger('log.json')

    def execute(self, request):
        try:
            assert isinstance(request, EnOSRequest)
            if Const.request_get == request.get_request_type():
                return EnOSRequest.get_response(self.do_get(request))
            elif Const.request_post == request.get_request_type():
                return EnOSRequest.get_response(self.do_post(request))
            else:
                raise RuntimeError("Unsupported request types")
        except Exception as x:
            self.__logging.error(x)
            raise x

    def do_get(self, request):
        url = self.__get_base_url(request)

        headers = {"content-type": request.get_content_type()}

        param_str = ''
        if request.replace_params_and_headers():
            param_str = request.get_replace_params_and_headers()
        else:
            params = request.get_params()
            if params is not None:
                assert isinstance(params, dict)
                for key in params:
                    if "orgId" == key or "requestTimestamp" == key:
                        pass
                    else:
                        param_str += "&"
                        param_str += key
                        param_str += "="
                        param_str += str(params[key])

        if len(param_str) > 0:
            url += param_str

        self.__logging.info("do get execute:%s", url)
        req = urllib2.Request(url, headers=headers)

        res_data = urllib2.urlopen(req, timeout=self.timeout)
        res = res_data.read()
        self.__logging.info("response :%s", res)
        return res

    def do_post(self, request):
        register_openers()
        url = self.__get_base_url(request)
        if request.replace_params_and_headers():
            data, headers = request.get_replace_params_and_headers()
        else:
            data = json.dumps(request.get_params())
            headers = {"content-type": request.get_content_type()}

        req = urllib2.Request(url, data=data, headers=headers)

        self.__logging.info("do post execute:%s ", url)
        res_data = urllib2.urlopen(req, timeout=self.timeout)
        res = res_data.read()
        self.__logging.info("response :%s", res)
        return res

    @staticmethod
    def setupBasicLogger(level='INFO', filePath=None,
                         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        if filePath is not None:
            logging.basicConfig(level=level, filename=filePath, format=format)
        else:
            logging.basicConfig(level=level, format=format)

    @staticmethod
    def setupFileLogger(filePath):
        path = filePath
        if os.path.exists(path):
            with open(path, "r") as f:
                config = json.load(f)
                logging.config.dictConfig(config)

    def __get_base_url(self, request):
        if self.url.endswith("/"):
            self.url = self.url[:-1]
        url = self.url + request.get_request_url()
        requestTimestamp = str(int(time.time() * 1000))
        params = request.get_params() if request.get_params() is not None else {}
        params["requestTimestamp"] = requestTimestamp
        params["orgId"] = request.org_id
        url = url + "?accessKey=" + self.access_key + "&requestTimestamp=" + str(
            int(time.time() * 1000)) + "&orgId=" + request.org_id + "&sign=" + Sign.sign(self.access_key,
                                                                                         self.secret_key,
                                                                                         params,
                                                                                         request.get_context_body())
        return url
