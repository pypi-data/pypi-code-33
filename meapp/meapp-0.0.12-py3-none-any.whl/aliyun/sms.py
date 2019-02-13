import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
client = AcsClient('LTAI2HCHy8kgiSjF', '6QK3LSMUxpSiXEoQjO8qv9150RDQ0o', 'default')

request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dysmsapi.aliyuncs.com')
request.set_method('POST')
request.set_protocol_type('https') # https | http
request.set_version('2017-05-25')
request.set_action_name('SendSms')


request.add_query_param('PhoneNumbers', '18687510604')
request.add_query_param('SignName', '老朱管理')
request.add_query_param('TemplateCode', 'SMS_66460074')
request.add_query_param('Format', 'json')
request.add_query_param('TemplateParam',json.dumps({'code':'1244'}))

from django.conf import settings

AliYunConfig = {
    'AccessKey':'2',
    'Secret':'1',
    'protocolType':'https'
}


try:
    if settings.AliYunConfig is not None:
        AliYunConfig = settings.ALIYUN
except Exception as e:
    pass


if not AliYunConfig['AccessKey']:
    raise Exception('please set AccessKey for AliYunConfig at setting')

if not AliYunConfig['Secret']:
    raise Exception('please set Secret for AliYunConfig at setting')

if not AliYunConfig['protocolType']:
    AliYunConfig['protocolType'] = "http"


class SingleSMS(object):
    mobiles = []
    signName = ''#老朱管理
    templateCode = ''#SMS_66460074
    templateParam = ''#

    protocolType = AliYunConfig['protocolType']

    def __init__(self,signName,templateCode,**params):
        self.signName = signName
        self.templateCode = templateCode
        for (key, value) in params.items():
            ext = 'self.%s = "%s"' % (key, value)
            # print(ext)
            exec(ext)

    def send(self,mobile,templateParam):
        client = AcsClient(AliYunConfig['AccessKey'], AliYunConfig['Secret'], 'default')

        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')

        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('PhoneNumbers', mobile)
        request.add_query_param('SignName', self.signName)
        request.add_query_param('TemplateCode', self.templateCode)
        request.add_query_param('Format', 'json')

        if isinstance(templateParam,dict):
            #templateParam = {'code':'1234'}
            request.add_query_param('TemplateParam', json.dumps(templateParam))
        else:
            request.add_query_param('TemplateParam', templateParam)

        response = client.do_action_with_exception(request)
        # response = client.do_action(request)


def SingleSMSTemplate(SignName,TemplateCode):

    class Template(SingleSMS):
        signName = SignName
        templateCode = TemplateCode

    return Template