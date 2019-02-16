from meapp.api.response import ApiResp,ApiState
from meapp.api.crawl import param_crawl
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from meapp.core.models import CodeRecord

class SmsView(ViewSet):
    @action(methods=['post', 'options', 'get'], detail=False)
    @param_crawl(checker={
        'mobile': {'n': True},
        'type': {'n': True}, # login | register
    })
    def sendCode(self,request):
        pass

