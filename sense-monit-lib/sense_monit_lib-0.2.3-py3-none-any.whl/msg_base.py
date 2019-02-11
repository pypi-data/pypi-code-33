#!/usr/bin/python
# -*- coding:utf-8 -*-

import uuid
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from aliyunsdkcore.request import RpcRequest
import json
import sense_core as sd

class SendSmsRequest(RpcRequest):
    def __init__(self):
        RpcRequest.__init__(self, 'Dysmsapi', '2017-05-25', 'SendSms')

    def get_TemplateCode(self):
        return self.get_query_params().get('TemplateCode')

    def set_TemplateCode(self,TemplateCode):
        self.add_query_param('TemplateCode',TemplateCode)

    def get_PhoneNumbers(self):
        return self.get_query_params().get('PhoneNumbers')

    def set_PhoneNumbers(self,PhoneNumbers):
        self.add_query_param('PhoneNumbers',PhoneNumbers)

    def get_SignName(self):
        return self.get_query_params().get('SignName')

    def set_SignName(self,SignName):
        self.add_query_param('SignName',SignName)

    def get_ResourceOwnerAccount(self):
        return self.get_query_params().get('ResourceOwnerAccount')

    def set_ResourceOwnerAccount(self,ResourceOwnerAccount):
        self.add_query_param('ResourceOwnerAccount',ResourceOwnerAccount)

    def get_TemplateParam(self):
        return self.get_query_params().get('TemplateParam')

    def set_TemplateParam(self,TemplateParam):
        self.add_query_param('TemplateParam',TemplateParam)

    def get_ResourceOwnerId(self):
        return self.get_query_params().get('ResourceOwnerId')

    def set_ResourceOwnerId(self,ResourceOwnerId):
        self.add_query_param('ResourceOwnerId',ResourceOwnerId)

    def get_OwnerId(self):
        return self.get_query_params().get('OwnerId')

    def set_OwnerId(self,OwnerId):
        self.add_query_param('OwnerId',OwnerId)

    def get_SmsUpExtendCode(self):
        return self.get_query_params().get('SmsUpExtendCode')

    def set_SmsUpExtendCode(self,SmsUpExtendCode):
        self.add_query_param('SmsUpExtendCode',SmsUpExtendCode)

    def get_OutId(self):
        return self.get_query_params().get('OutId')

    def set_OutId(self,OutId):
        self.add_query_param('OutId',OutId)


# 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"
ACCESS_KEY_ID = sd.config('aliyun_sms','key_id')
ACCESS_KEY_SECRET = sd.config('aliyun_sms','key_secret')

acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
# region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)
region_provider.modify_point(PRODUCT_NAME, REGION, DOMAIN)

def send_sms(phone_numbers, template_code, template_param=None):
    print(phone_numbers, template_code, template_param)
    business_id = uuid.uuid4()
    sign_name = sd.config('aliyun_sms','name')

    sms_request = SendSmsRequest()  # 申请的短信模板编码,必填
    sms_request.set_TemplateCode(template_code)  # 短信模板变量参数
    if template_param is not None:
        sms_request.set_TemplateParam(template_param)
    sms_request.set_OutId(business_id)  # 设置业务请求流水号，必填。
    sms_request.set_SignName(sign_name)  # 短信签名
    sms_request.set_PhoneNumbers(phone_numbers)  # 短信发送的号码列表，必填。
    sms_response = acs_client.do_action_with_exception(sms_request)  # 调用短信发送接口，返回json

    return sms_response

# if __name__ == '__main__':
#     params = {'code': 1, 'message': '模块{}一小时内错误数:{}, 请及时解决.'}
#     print(send_sms("18252064545", "SMS_154505884", params))
    #print(send_sms(__business_id, "13000000000", "云通信测试", "SMS_5250008", params))
