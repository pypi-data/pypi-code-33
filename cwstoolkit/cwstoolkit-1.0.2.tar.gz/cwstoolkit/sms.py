#!/usr/bin/env python
#encoding: utf-8
# Author: colinspace
# Date: 2018
# Desc:
#

from yunpian_python_sdk.ypclient import YunpianClient
from yunpian_python_sdk.model import constant as YC

from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import SendBatchSmsRequest
from aliyunsdkcore.profile import region_provider

# import configparser
import uuid
import sys

if sys.version_info.major == 2:
    from urllib import urlencode
    import ConfigParser as configparser
elif sys.version_info.major == 3:
    from  urllib.parse import urlencode 
    import configparser

# import urllib.parse
# import serverMonitor


class SMS():
    """
    @param: sms_config_file:  sms.conf config file 
    @param: mobile
    @param: content
    @return: sendstatus

    ## warn
    告警 - 资源[${resource}]；当前值[${currentValue}] - 阈值[${threshold}]；备注：${remark}
    {"resouce": "cpu", "currentValue": "95%", "threshold": "80%", "remark": "192.168.2.52 4core"}

    ## recovery
    恢复 - 资源[${resource}]；当前值[${currentValue}]；备注：${remark}
    {"resouce": "cpu", "currentValue": "2.3%", "remark": "192.168.2.4"}
    """

    def __init__(self, sms_config_file='/etc/.sms.conf',section='sms', mobile=None, content=None, smstype='warn'):
        self.sms_config_file = sms_config_file
        self.section = section
        self.mobile = mobile
        self.content = content
        self.smstype = smstype



    def getYunpianConfig(self):
        config = configparser.ConfigParser()
        config.read(self.sms_config_file)
        return config['yunpiansms']['api_key']

    def getAliyunConfig(self):
        aliyunsms = {}
        config = configparser.ConfigParser()
        config.read(self.sms_config_file)
        aliyunsms['access_keyid'] = config.get(self.section, 'access_keyid')
        aliyunsms['access_keysecret'] = config.get(self.section, 'access_keysecret')
        aliyunsms['template_code_warn'] = config.get(self.section, 'template_code_warn')
        aliyunsms['template_code_recovery'] = config.get(self.section, 'template_code_recovery')
        aliyunsms['sign_name'] = config.get(self.section, 'sign_name')
        return aliyunsms

 
    def yunpianSMS(self):
        """
        云片短信发送
        内容模板：
        {"resource": "CPU", "detail": "the detail of warning info", "remark": "could be empty"}
        """
        msg = {}
        apikey = self.getYunpianConfig()
        client = YunpianClient(apikey)

        # mobile template id
        if self.smstype == 'warn':
            template_id =  2651642
        elif self.smstype == 'recovery':
            template_id =  2651644

        # template_id = 2265948

        # mobile template value
        # template_value = urllib.parse.urlencode(eval(self.content)) 
        template_value = urlencode(eval(self.content)) 

        # build param
        param = {YC.MOBILE:self.mobile, YC.TPL_ID:template_id, YC.TPL_VALUE:template_value}

        # single or batch to send 
        if len(self.mobile.split(',')) > 1:
            result = client.sms().tpl_batch_send(param)
        else:
            result = client.sms().tpl_single_send(param)

        # check if send successful
        if result.code() == 0:
            msg['code'] = 200
            msg['msg'] = "yunpian sms send sucessfully!"
        else:
            msg['code'] = 5003
            msg['msg'] = "Sorry, send sms failed! Exception like: %s" % res.exception

        return msg 


    

    def aliyunSMS(self):
        """
        阿里云发送短信
        """
        msg = []

        REGION = "cn-hangzhou"
        PRODUCT_NAME = "Dysmsapi"
        DOMAIN = "dysmsapi.aliyuncs.com"

        aliyunconfig = self.getAliyunConfig()
        access_keyid = aliyunconfig['access_keyid']
        access_keysecret = aliyunconfig['access_keysecret']
        template_code_warn = aliyunconfig['template_code_warn']
        template_code_recovery = aliyunconfig['template_code_recovery']
        sign_name = aliyunconfig['sign_name']
        # uid = aliyunconfig['UID']
        uid = uuid.uuid1()

        acs_client = AcsClient(access_keyid, access_keysecret, REGION)
        region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)
        if self.smstype == 'warn':
            template_code = template_code_warn
        elif self.smstype == 'recovery':
            template_code = template_code_recovery
        smsRequest = SendSmsRequest.SendSmsRequest()
        smsRequest.set_TemplateCode(template_code)
        smsRequest.set_SignName(sign_name) 
        smsRequest.set_OutId(uid)
        smsRequest.set_TemplateParam(self.content)

        for number in self.mobile.split(','):
            msg_temp = {}
            smsRequest.set_PhoneNumbers(number)
            smsResponse = eval(acs_client.do_action_with_exception(smsRequest).decode('utf-8'))
            if smsResponse['Message'] == 'OK':
                msg_temp['code'] = 200
                msg_temp['msg'] = "Aliyun sms send sucessfully!"
            else:
                msg_temp['code'] = 5004
                msg_temp['msg'] = "Sorry, send sms failed! Exception like: %s" % smsResponse['Message']
            msg.append(msg_temp)

        return msg 


