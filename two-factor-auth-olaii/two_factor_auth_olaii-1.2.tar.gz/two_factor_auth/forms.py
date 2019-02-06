from binascii import unhexlify
from time import mktime
import datetime
import hashlib
import hmac
from base64 import b32encode
import base64

from django import forms
from django.forms import Form
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_otp.forms import OTPAuthenticationFormMixin

from two_factor_auth.models import Totp, generate_key
from two_factor_auth.utils import strings_equal


class MethodForm(forms.Form):
    method = forms.ChoiceField(label=_("Method"),
                               initial='generator',
                               widget=forms.RadioSelect)

    def __init__(self, **kwargs):
        super(MethodForm, self).__init__(**kwargs)
        self.fields['method'].choices = [('generator', _('Token generator'))]


class DeviceValidationForm(forms.Form):
    token = forms.IntegerField(label=_("Token"), min_value=1, max_value=int('9' * getattr(settings, 'TOTP_DIGITS', 6)))

    error_messages = {
        'invalid_token': _('Entered token is not valid.'),
    }

    def __init__(self, totp, **args):
        super(DeviceValidationForm, self).__init__(**args)
        self.totp = totp

    def clean_token(self):
        token = self.cleaned_data['token']
        if not self.totp.verify_token(token):
            raise forms.ValidationError(self.error_messages['invalid_token'])
        return token


class TOTPDeviceForm(forms.Form):
    token = forms.IntegerField(label=_("Token"), min_value=0, max_value=int('9' * getattr(settings, 'TOTP_DIGITS', 6)))

    error_messages = {
        'invalid_token': _('Entered token is not valid.'),
    }

    def __init__(self, key, user, metadata=None, **kwargs):
        super(TOTPDeviceForm, self).__init__(**kwargs)
        self.user = user
        self.key = key
        self.tolerance = 0
        self.t0 = 0
        self.step = 30
        self.drift = 0
        self.digits = settings.TOTP_DIGITS
        self.metadata = metadata or {}

    @property
    def bin_key(self):
        """
        The secret key as a binary string.
        """
        return unhexlify(self.key.encode())

    def clean_token(self):
        token = self.cleaned_data.get('token')
        for_time = datetime.datetime.now()
        validated = False

        token = str(token)
        while len(token) < settings.TOTP_DIGITS:
            token = '0' + token

        for i in range(-self.tolerance, self.tolerance + 1):
            if strings_equal(str(token), str(int(self.at(for_time, i)))):
                validated = True

        if not validated:
            raise forms.ValidationError(self.error_messages['invalid_token'])
        return token

    def save(self):
        totp, created = Totp.objects.update_or_create(user=self.user)
        totp.secret = self.key
        totp.backup_key = generate_key()
        totp.enabled = True
        totp.save()

        return totp

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
            raise forms.ValidationError(self.error_messages['invalid_token'])
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

    def timecode(self, for_time):
        i = mktime(for_time.timetuple())
        return int(i / self.step)

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

class DisableForm(forms.Form):
    understand = forms.BooleanField(label=_("Yes, I am sure"))


#class AuthenticationTokenForm(Form):
class AuthenticationTokenForm(OTPAuthenticationFormMixin, Form):
    otp_token = forms.IntegerField(label=_("Token"), min_value=1,
                                   max_value=int('9' * getattr(settings, 'TOTP_DIGITS', 6)))

    otp_token.widget.attrs.update({'autofocus': 'autofocus'})

    # Our authentication form has an additional submit button to go to the
    # backup token form. When the `required` attribute is set on an input
    # field, that button cannot be used on browsers that implement html5
    # validation. For now we'll use this workaround, but an even nicer
    # solution would be to move the button outside the `<form>` and into
    # its own `<form>`.
    use_required_attribute = False

    def __init__(self, user, initial_device, **kwargs):
        """
        `initial_device` is either the user's default device, or the backup
        device when the user chooses to enter a backup token. The token will
        be verified against all devices, it is not limited to the given
        device.
        """
        super(AuthenticationTokenForm, self).__init__(**kwargs)
        self.user = user


    def clean(self):
        self.clean_otp(self.user)
        return self.cleaned_data


class BackupTokenForm(AuthenticationTokenForm):
    otp_token = forms.CharField(label=_("Token"))
