# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     config
   Description :
   Author :       潘晓华
   date：          2019/1/15
-------------------------------------------------
"""


class ApiConfig(object):
    api_drivers = 'qingcloud'
    # api请求域名
    api_domain = 'http://api.cloud.example.com/iaas'

    # 平台帐号key与secret key
    api_access_key_id = ''
    api_secret_access_key = ''

    # API版本号
    api_version = '1'

    # 签名版本号
    api_signature_version = '1'

    # 加密方式，支持'HmacSHA256'与'HmacSHA1'
    api_signature_method = 'HmacSHA256'

    # 目前api_ssl_crt这个没有用
    api_ssl_crt = 'ssl.crt'

    # 默认的zone
    api_default_zone = 'SHA'

    @classmethod
    def config(cls, api_drivers=None, api_domain=None, api_access_key_id=None, api_secret_access_key=None, api_default_zone=None):
        """
        设置配置参数
        :param api_drivers: 驱动名
        :param api_domain: Iaas Host
        :param api_access_key_id: access key
        :param api_secret_access_key: secret key
        :return:
        """
        if api_drivers:
            ApiConfig.api_drivers = api_drivers
        if api_domain:
            ApiConfig.api_domain = api_domain
        if api_access_key_id:
            ApiConfig.api_access_key_id = api_access_key_id
        if api_secret_access_key:
            ApiConfig.api_secret_access_key = api_secret_access_key
        if api_default_zone:
            ApiConfig.api_default_zone = api_default_zone