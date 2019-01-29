import json
import random
import string
from datetime import datetime, timedelta

import twilio.rest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
from phonenumber_field.validators import validate_international_phonenumber
from twilio.base.exceptions import TwilioRestException

from ccc.users.models import OTPStore, UserProfile


def send_twilio_message(to_number, body):
    try:
        if settings.SEND_TWILIO_MSG:
            client = twilio.rest.Client(
                settings.TWILIO_SID,
                settings.TWILIO_TOKEN
            )

            client.messages.create(
                body=body,
                to=to_number,
                from_=settings.OTP_PHONE_NUMBER
            )
        print("\n\n\nMessage Sent {}".format(body))
        return True
    except TwilioRestException as e:
        print("Error occurred while sending message", e)
        raise e
    except Exception as e:
        print("Unknown error ", e)
        raise e


def send_otp(phone_number=None, lang="en"):
    key = ""
    for x in range(1, 6):
        key += random.choice(string.digits)
        # Instantiate a Verify object.
    body = "One time password for Cloud Custom Connection login is {}".format(key)
    try:
        OTPStore.objects.create(phone_no=phone_number, otp=key)
    except IntegrityError as ex:
        OTPStore.objects.filter(phone_no=phone_number).update(
            otp=key, timestamp=datetime.now())

    status = send_twilio_message(phone_number, body)
    return status


def verify_phone(request, phone_num, lang="en"):
    statusresult, ex = send_otp(phone_num, lang)
    return HttpResponse(json.dumps({"results": [{"status": statusresult}]}))


def verify_otp(request, phone_num, otp_code):
    query_set = OTPStore.objects.filter(phone_no=phone_num, otp=otp_code)
    result = query_set.count()
    status = False
    msg = _("Provided Code is incorrect")
    if result > 0:
        time_threshold = datetime.now() - timedelta(hours=1)
        if query_set.filter(timestamp__gt=time_threshold).count() > 0:
            status = True
            msg = _("Verification completed successfully")
            user_filter = UserProfile.objects.filter(phone=phone_num)
            if user_filter.exists():
                # Assuming that we will get one record as phone wll be unique
                user = user_filter[0]
                if not user.is_phone_verified:
                    user.is_phone_verified = True
                    user.save()
        else:
            msg = _("Provided Code has already expired")
    if settings.TEST_ENV:
        status = True

    return {"results": {"status": status,
                        "msg": str(msg)
                        }
            }


def validate_user_phone(phone):
    validate_international_phonenumber(phone)
    if UserProfile.objects.filter(phone=phone).exists():
        raise ValidationError(_(u'The phone number entered already registered with another user.'))


def set_cookie(response, key, value, days_expire=7):
    """Set cookie helper function"""
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")

    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None
    )
