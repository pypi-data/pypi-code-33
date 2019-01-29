from random import randint

from django.conf import settings
from django.db.models import Q
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioRestClient

from ccc.packages.models import TwilioNumber

"""
All these functions are legacy and bad code that I didn't wrote. #Todo pending 
refactor this and another pieces of code
"""

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


def get_obj_from_twilio_number(twilio_number):
    """
    Get Object twilio number. #Todo, where is the doc??
    """
    twilio_no_obj = None
    twilio_qs = TwilioNumber.objects.filter(Q(twilio_number=twilio_number) | Q(friendly_name=twilio_number))

    if twilio_qs.exists():
        twilio_no_obj = twilio_qs[0]

    return twilio_no_obj


def get_random_twilio_number(exclude_number_list=[], sms_enabled=None, mms_enabled=None):
    """
    #TODO Where is the doc ???
    """
    queryset = TwilioNumber.objects.exclude(
        Q(twilio_number__in=exclude_number_list) |
        Q(friendly_name__in=exclude_number_list) |
        Q(twilio_number__isnull=True)
    )

    if sms_enabled is not None:
        queryset = queryset.filter(sms_enabled=sms_enabled)

    if mms_enabled is not None:
        queryset = queryset.filter(mms_enabled=mms_enabled)

    count = queryset.count()

    try:
        random_index = randint(0, count - 1)
        return queryset[random_index]
    except BaseException:
        return None


def check_and_set_throttle(value=None, clear_exisitng=False):
    # Here was a lot of DEAD CODE from legacy, I'm only copy this function for reason of pass test #todo delete
    pass
