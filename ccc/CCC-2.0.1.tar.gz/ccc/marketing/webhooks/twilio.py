import logging

from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from ccc.campaigns.models import OSMS

logger = logging.getLogger(__name__)


class TwilioWebHookSMSStatus(APIView):
    """Twilio webhook SMS status"""
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, *args, **kwargs):
        message_sid = self.request.data.get('MessageSid', None)
        message_status = self.request.data.get('MessageStatus', None)
        logging.info('SID: {}, Status: {}'.format(message_sid, message_status))

        if message_sid and message_status:
            sms = OSMS.objects.get(message_sid=message_sid)
            sms.status = message_status
            sms.save()
        return Response({'message': 'Succes!. Thanks twilio'})
