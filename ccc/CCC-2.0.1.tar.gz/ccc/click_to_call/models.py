# -*- coding: utf-8 -*-
import logging
from logging import getLogger

import requests
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ccc.click_to_call.contants import REAL_PHONE_STATUSES, REAL_PHONE_TYPE

log = getLogger(__name__)


class TwimlApplication(models.Model):
    sid = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sid


class AssociateMasterList(models.Model):
    """Model to store Autodial list
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    is_import_complete = models.BooleanField(default=False)
    has_errors = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.user.email)


class AutoDialerList(models.Model):
    """Table to store Autodial number

    As a Users Should be able to view the calling data. First name, Last Name, Phone Number, City, State, phone type landline or cell
    """
    first_name = models.CharField(max_length=50, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=50, blank=True, null=True, default=None)
    city = models.CharField(max_length=50, blank=True, null=True, default=None)
    state = models.CharField(max_length=50, blank=True, null=True, default=None)

    associated_to = models.ForeignKey(AssociateMasterList, on_delete=models.CASCADE)
    is_processed = models.BooleanField(default=False)

    # Phone data validation
    phone_friendly_number = models.CharField(max_length=255, blank=True, null=True,
                                             help_text="Phone Number in nice format")
    phone_number = models.CharField(max_length=25, blank=True, null=True, editable=False,
                                    help_text="Phone number without spaces, dashes, or non-numeric characters.")

    phone_status = models.CharField(max_length=50, choices=REAL_PHONE_STATUSES, blank=True, null=True, default=None)

    phone_type = models.CharField(max_length=10, choices=REAL_PHONE_TYPE, blank=True, null=True, default='', )
    phone_carrier = models.CharField(max_length=100, blank=True, null=True, default="")
    phone_cname = models.CharField(max_length=100, blank=True, null=True, default="",
                                   help_text="The caller ID of the phone")

    is_valid = models.BooleanField()
    msg_err = models.TextField(null=True, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} ({})".format(self.phone_number, self.associated_to)


class CallHistory(models.Model):
    """Model to store call history
    """
    number = models.ForeignKey(AutoDialerList, on_delete=models.CASCADE)
    dialed_time = models.DateTimeField(default=None, blank=True, null=True)
    call_duration_in_seconds = models.IntegerField(default=0)

    def __str__(self):
        return "{}".format(self.number)


class RealPhoneValidation(models.Model):
    """RealPhoneValidation is our local repository of the service RealPhoneValidation,
    to avoid call the API for previous validation, need to define a mechanism of update."""

    phone_number = models.CharField(max_length=25, editable=False,
                                    help_text="Phone number without spaces, dashes, or non-numeric characters.")
    phone_country_code = models.CharField(max_length=5, blank=True, null=True)
    phone_friendly_number = models.CharField(max_length=255, blank=True, null=True,
                                             help_text="Phone Number in nice format")
    phone_status = models.CharField(max_length=50, choices=REAL_PHONE_STATUSES, blank=True, null=True, default=None)

    phone_type = models.CharField(max_length=10, choices=REAL_PHONE_TYPE, blank=True, null=True, default='', )
    phone_carrier = models.CharField(max_length=100, blank=True, null=True, default="")
    phone_cname = models.CharField(max_length=100, blank=True, null=True, default="",
                                   help_text="Caller ID")

    last_updated = models.DateTimeField(auto_now_add=True)

    error_text = models.TextField(max_length=500, blank=True, null=True, default="")

    def __str__(self):
        return "{}".format(self.phone_number)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.phone_number = str(self.phone_number)
            self._format_friendly_number()
            self.turbo_validation()
        super(RealPhoneValidation, self).save(*args, **kwargs)

    def _format_friendly_number(self):
        """Return a friendly PhoneNumber format"""
        try:
            self.phone_friendly_number = "({0[0]}{0[1]}{0[2]}) {0[3]}{0[4]}{0[5]}-{0[6]}{0[7]}{0[8]}{0[9]}".format(
                tuple(str(self.phone_number)))
        except Exception as e:
            logging.error(e.__str__())

    def turbo_validation(self):
        """Real Phone Turbo validation API Option"""
        url = settings.API_REALPHONE_VALIDATION + '/rpvWebService/RealPhoneValidationTurbo.php'
        is_cell = {'Y': 'landline', 'N': 'cell-phone', 'V': 'voip'}

        payload = {
            'output': 'json',
            'phone': self.phone_number,
            'token': settings.TOKEN_REALPHONE_VALIDATION
        }
        r = requests.get(url, payload)
        resp = r.json()

        self.phone_carrier = resp["carrier"]
        self.phone_status = resp["status"]
        self.phone_cname = resp['cnam']
        self.phone_type = is_cell[resp['iscell']]
        self.error_text = str(resp['error_text'])

        return r.status_code

    def is_valid(self):
        return True


class PersonalizedMessage(models.Model):
    MESSAGE_TYPES = (
        (_('sms'), 'Text Message'),
        (_('voice'), 'Voice Message'),
    )
    name = models.CharField(max_length=255)
    type = models.CharField(choices=MESSAGE_TYPES, max_length=5, default=MESSAGE_TYPES[1][0])
    audio = models.FileField(upload_to='calls/personalized', null=True)
    text = models.CharField(default='', max_length=1000)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    audio_processed = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
