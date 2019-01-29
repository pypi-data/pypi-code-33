# coding: utf-8
"""
This module contains PhoneNumber objects and a set of utilites that allows
handling easily SMS and Voice.
"""

import logging

from django.shortcuts import get_object_or_404

from ccc.campaigns.models import RedirectNumber, RejectedNumber
from ccc.packages.models import TwilioNumber

logger = logging.getLogger(__name__)


def get_reject_numbers(phone_number):
    return RejectedNumber.objects.filter(reject_number=phone_number)


class PhoneNumber(object):
    """Represent a valid twillio phone line number"""

    def __init__(self, number):
        self.number = number

    def is_reject(self, called):
        """Returns True if the number (caller or called) is from
        which we don't to receive call or SMS"""

        reject_numbers = get_reject_numbers(self.number)
        if reject_numbers.exists():
            reject_number = reject_numbers[0]
            if reject_number.reject_for_all:
                return True
            elif reject_number.twilio_numbers.filter(twilio_number=called).exists():
                return True
        return False


class TwilioPhoneNumber(object):
    """Wrap a valid twillio number"""

    def __init__(self, number):
        self.obj = get_object_or_404(TwilioNumber, twilio_number=number)

    @property
    def redirect(self):
        """Returns True if twillio number has enabled 'redirect' and has a redirect number assigned"""
        if self.obj.is_redirected and self.get_redirect_number():
            return True

    @property
    def number(self):
        return self.obj.twilio_number

    def get_redirect_number(self):
        return RedirectNumber.objects.filter(from_no=self.obj.twilio_number).first()
