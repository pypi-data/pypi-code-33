import json
from meapp.api.response import ApiState,ApiResp
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from django.conf import settings

AliYunConfig = {
    'AccessKey':'',
    'Secret':'',
    'protocolType':'https'
}


try:
    if settings.ALIYUN is not None:
        AliYunConfig = settings.ALIYUN
except Exception as e:
    pass


if not AliYunConfig['AccessKey']:
    raise Exception('please set AccessKey for ALIYUN at setting')

if not AliYunConfig['Secret']:
    raise Exception('please set Secret for ALIYUN at setting')

if not AliYunConfig['protocolType']:
    AliYunConfig['protocolType'] = "http"


class SingleSMS(object):
    mobiles = []
    signName = ''#老朱管理
    templateCode = ''#SMS_66460074
    templateParam = ''#

    protocolType = AliYunConfig['protocolType']

    def __init__(self,**params):
        for (key, value) in params.items():
            ext = 'self.%s = "%s"' % (key, value)
            # print(ext)
            exec(ext)

    def send(self,mobile,templateParam):
        code = 'except'

        try:
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

            try:
                response = client.do_action_with_exception(request)
                rsp = str(response, encoding='utf-8')
                obj = json.loads(rsp);
                code = obj['Code'] + ""
                code = code.lower()
                return (ApiState.success,code)
            except Exception as e:
                return (ApiState.exception, code)

        except Exception as e:
            return (ApiState.exception,code)



def SingleSMSTemplate(SignName,TemplateCode):

    class Template(SingleSMS):
        signName = SignName
        templateCode = TemplateCode

    return Template