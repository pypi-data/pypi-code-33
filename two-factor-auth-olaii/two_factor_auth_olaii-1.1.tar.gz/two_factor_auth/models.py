from __future__ import unicode_literals

import base64
import hashlib
import hmac
from base64 import b32encode
import datetime
import time
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.encoding import force_text
from django.utils.six import string_types
from django.utils.six.moves.urllib.parse import quote, urlencode
from django.utils.crypto import constant_time_compare
from django_otp.models import Device

from two_factor_auth.utils import random_hex, hex_validator, unhexlify, strings_equal


def default_key():
    return force_text(random_hex(20))

def key_validator(value):
    return hex_validator()(value)

def generate_key():
    """Generates a key used for secret keys."""
    return uuid4().hex


class Totp(Device):
    secret = models.CharField(null=False, blank=False, default=default_key, validators=[key_validator], max_length=50, help_text="Hex-encoded secret key")
    interval = models.PositiveSmallIntegerField(default=30)
    backup_key = models.CharField(max_length=32, default=generate_key, blank=True, help_text="Hex-Encoded Secret Key")
    enabled = models.BooleanField(default=False, blank=False, null=False)

    @property
    def bin_key(self):
        """
        The secret key as a binary string.
        """
        return unhexlify(self.secret.encode())

    @property
    def config_url(self):
        """
        A URL for configuring Google Authenticator or similar.

        See https://github.com/google/google-authenticator/wiki/Key-Uri-Format.
        The issuer is taken from :setting:`TOTP_ISSUER`, if available.

        """
        label = self.user.email
        params = {
            'secret': b32encode(self.bin_key),
            'algorithm': 'SHA1',
            'digits': getattr(settings, 'TOTP_DIGITS', 6),
            'period': self.interval,
        }

        issuer = getattr(settings, 'TOTP_ISSUER', None)
        if isinstance(issuer, string_types) and (issuer != ''):
            issuer = issuer.replace(':', '')
            params['issuer'] = issuer
            label = '{}:{}'.format(issuer, label)

        url = 'otpauth://totp/{}?{}'.format(quote(label), urlencode(params))

        return url

    @property
    def backup_code(self):
        """Returns the users backup code."""
        return self.backup_key.upper()[:settings.TOTP_DIGITS]

    def verify_token(self, otp, for_time=None, valid_window=0):
        """
        Verifies the OTP passed in against the current time OTP.

        :param otp: the OTP to check against
        :type otp: str
        :param for_time: Time to check OTP at (defaults to now)
        :type for_time: int or datetime
        :param valid_window: extends the validity to this many counter ticks before and after the current one
        :type valid_window: int
        :returns: True if verification succeeded, False otherwise
        :rtype: bool
        """

        # custom code for admin login, where backup code is also checked with call verify_token
        backup = self.backup_code
        if otp and constant_time_compare(otp, backup):
            self.enabled = False
            self.save()
            return True

        if for_time is None:
            for_time = datetime.datetime.now()

        otp = str(otp)
        while len(otp) < settings.TOTP_DIGITS:
            otp = '0' + otp

        if valid_window:
            for i in range(-valid_window, valid_window + 1):
                if strings_equal(str(otp), str(int(self.at(for_time, i)))):
                    self.enabled = True
                    self.save()
                    return True
            return False

        verified = strings_equal(str(otp), str(self.at(for_time)))
        if verified:
            self.enabled = True
            self.save()

        return verified

    def at(self, for_time, counter_offset=0):
        """
        Accepts either a Unix timestamp integer or a datetime object.

        :param for_time: the time to generate an OTP for
        :type for_time: int or datetime
        :param counter_offset: the amount of ticks to add to the time counter
        :returns: OTP value
        :rtype: str
        """
        if not isinstance(for_time, datetime.datetime):
            for_time = datetime.datetime.fromtimestamp(int(for_time))
        return self.generate_otp(self.timecode(for_time) + counter_offset)

    def generate_otp(self, input):
        """
        :param input: the HMAC counter value to use as the OTP input.
            Usually either the counter, or the computed integer based on the Unix timestamp
        :type input: int
        """
        if input < 0:
            raise ValueError('input must be positive integer')
        hasher = hmac.new(self.byte_secret(), self.int_to_bytestring(input), hashlib.sha1)
        hmac_hash = bytearray(hasher.digest())
        offset = hmac_hash[-1] & 0xf
        code = ((hmac_hash[offset] & 0x7f) << 24 |
                (hmac_hash[offset + 1] & 0xff) << 16 |
                (hmac_hash[offset + 2] & 0xff) << 8 |
                (hmac_hash[offset + 3] & 0xff))
        str_code = str(code % 10 ** settings.TOTP_DIGITS)
        while len(str_code) < settings.TOTP_DIGITS:
            str_code = '0' + str_code

        return str_code

    def byte_secret(self):
        secret_b32encode = b32encode(self.bin_key)
        missing_padding = len(secret_b32encode) % 8
        if missing_padding != 0:
            secret_b32encode += '=' * (8 - missing_padding)
        return base64.b32decode(secret_b32encode, casefold=True)

    @staticmethod
    def int_to_bytestring(i, padding=8):
        """
        Turns an integer to the OATH specified
        bytestring, which is fed to the HMAC
        along with the secret
        """
        result = bytearray()
        while i != 0:
            result.append(i & 0xFF)
            i >>= 8
        # It's necessary to convert the final result from bytearray to bytes
        # because the hmac functions in python 2.6 and 3.3 don't work with
        # bytearray
        return bytes(bytearray(reversed(result)).rjust(padding, b'\0'))

    def refresh_backup_code(self):
        """
        Refreshes the users backup key and returns a new backup code.

        This method should be used to request new backup codes for the user.
        """
        assert self.enabled, (
            "MFA must be on to run refresh_backup_codes."
        )
        self.backup_key = generate_key()
        self.save()
        return self.backup_code

    def check_and_use_backup_code(self, code):
        """
        Checks if the inputted backup code is correct and disables MFA if
        the code is correct.

        This method should be used for authenticating with a backup code. Using
        a backup code to authenticate disables MFA as a side effect.
        """
        backup = self.backup_code
        if code and constant_time_compare(code, backup):
            self.enabled = False
            self.save()
            return True
        return False

    def timecode(self, for_time):
        i = time.mktime(for_time.timetuple())
        return int(i / self.interval)

    def has_backup_code(self):
        if self.backup_key != "":
            return True
        else:
            return False

