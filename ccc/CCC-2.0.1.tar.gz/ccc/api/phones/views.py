from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client as TwilioRestClient

from ccc.api.helpers import ApiResponse, request_parse
from ccc.api.phones.models import Number
from ccc.api.phones.serializers import NumberSerializer


def search(request, area_code):
    client = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    numbers = client.phone_numbers.search(area_code=area_code)[:10]
    resp_data = {'numbers': [{'friendly_name': no.friendly_name, 'phone_number': no.phone_number} for no in numbers]}
    return ApiResponse(resp_data)


def list(request):
    numbers = request.user.numbers.all()
    serializer = NumberSerializer(numbers, many=True)
    return ApiResponse(serializer.data)


@csrf_exempt
def add(request):
    client = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    post_data = request_parse(request)
    try:
        number = post_data.get('number')
        notes = post_data.get('notes', "")

        # Purchase a number on twilio
        twilio_no = client.phone_numbers.purchase(phone_number=number['phone_number'])

        # Add webhooks to number
        # change gateway domain in /champion/settings.py
        # GATEWAY_DOMAIN = 'http://lab.duythinht.com'

        voice_url = settings.GATEWAY_DOMAIN + '/gateway/voice'
        sms_url = settings.GATEWAY_DOMAIN + '/gateway/sms'
        twilio_no.update(voice_url=voice_url, sms_url=sms_url)

        # Everything is ok? Save data to database

        num = Number()
        num.user = request.user
        num.sid = twilio_no.sid
        num.phone_no = number['phone_number']
        num.friendly_name = number['friendly_name']
        num.notes = notes
        num.save()

        return ApiResponse({'Done': True})
    except BaseException:
        return ApiResponse({'Fail': True}, status=400)
