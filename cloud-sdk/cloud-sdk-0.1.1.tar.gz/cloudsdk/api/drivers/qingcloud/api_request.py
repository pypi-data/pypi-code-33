# coding=utf-8
"""
    生成请求链接
    @author 潘晓华
    @written at 2017-08-02 10:00am
"""
import base64
import hmac
import time
from hashlib import sha256, sha1
from urllib import quote, quote_plus, urlencode

from cloudsdk.config import ApiConfig


class ApiRequest(object):
    @classmethod
    def build_url(cls, params={}, method='GET'):
        # 生成请求链接
        time_stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        params_input = dict(params)
        params_input['time_stamp'] = time_stamp
        params_input['access_key_id'] = ApiConfig.api_access_key_id
        params_input['version'] = ApiConfig.api_version
        params_input['signature_method'] = ApiConfig.api_signature_method
        params_input['signature_version'] = ApiConfig.api_signature_version
        if ('zone' not in params_input.keys()):
            params_input['zone'] = ApiConfig.api_default_zone

        params_string, signature = cls.__signature_params(params_input, method)
        params_input['signature'] = signature
        params_string += 'signature=' + signature
        return ApiConfig.api_domain, params_string

    @classmethod
    def __signature_params(cls, sign_params, method):
        # 对参数进行签名生成
        params_to_string = ''
        for k in sorted(sign_params.keys()):
            params_to_string += urlencode({k: str(sign_params[k])}) + '&'
        params_string_add_header = method.upper() + '\n/iaas/\n' + params_to_string[:-1]
        if ApiConfig.api_signature_method == 'HmacSHA256':
            h = hmac.new(ApiConfig.api_secret_access_key, digestmod=sha256)
        elif ApiConfig.api_signature_method == 'HmacSHA1':
            h = hmac.new(ApiConfig.api_secret_access_key, digestmod=sha1)
        h.update(params_string_add_header)
        sign = base64.b64encode(h.digest()).strip()
        signature = quote_plus(sign)
        return params_to_string, signature
