from django import forms
from django.conf import settings

from ccc.users.models import UserProfile
from ccc.users.utils import validate_user_phone, verify_otp


class VerifyOtpForm(forms.Form):
    """
    Verify OTP password
    """
    otp = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(VerifyOtpForm, self).__init__(*args, **kwargs)
        self.fields['otp'].widget = forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid placeholder-no-fix',
                'placeholder': 'Enter one time password to verify',
                'autocomplete': 'off'
            }
        )

    def clean_otp(self):
        """
        Validate OTP
        """
        otp = self.cleaned_data['otp']

        phone_num = self.request.user.phone.as_e164
        results = verify_otp(self.request, phone_num, otp)
        results = results['results']
        if not results['status']:
            raise forms.ValidationError(results['msg'])
        return otp


class UpdatePhoneForm(forms.Form):
    """
    Verify OTP password
    """
    phone = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UpdatePhoneForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget = forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid placeholder-no-fix',
                'placeholder': 'Enter phone without country code',
                'autocomplete': 'off'
            }
        )

    def clean_phone(self):
        """
        Validate Phone number
        """
        code = settings.DEFAULT_COUNTRY_PHONE
        phone = "{}{}".format(code, self.cleaned_data['phone'])
        validate_user_phone(phone)
        return phone


class SubAccountForm(forms.ModelForm):
    """Add Sub account form"""
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'parent', 'company_name')
        widgets = {'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
                   'parent': forms.HiddenInput(), 'company_name': forms.HiddenInput()}
