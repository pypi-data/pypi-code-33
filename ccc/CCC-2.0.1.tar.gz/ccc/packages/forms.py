import re
from calendar import monthrange
from datetime import date

from django import forms
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError

from ccc.billing.models import Customer
from ccc.campaigns.models import RedirectNumber
from ccc.packages.models import PackageType, TwilioNumber


class CreditCardField(forms.IntegerField):
    def clean(self, value):
        """Check if given CC number is valid and one of the
           card types we accept"""
        if value and (len(value) < 13 or len(value) > 16):
            raise forms.ValidationError("Please enter in a valid "
                                        "credit card number.")
        return super(CreditCardField, self).clean(value)


class CCExpWidget(forms.MultiWidget):
    """ Widget containing two select boxes for selecting the month and year"""

    def decompress(self, value):
        return [value.month, value.year] if value else [None, None]

    def format_output(self, rendered_widgets):
        html = u' / '.join(rendered_widgets)
        return u'<span style="white-space: nowrap;">%s</span>' % html


class CCExpField(forms.MultiValueField):
    EXP_MONTH = [(x, str(x).zfill(2)) for x in range(1, 13)]
    EXP_YEAR = [(x, x % 100) for x in range(date.today().year,
                                            date.today().year + 15)]
    default_error_messages = {
        'invalid_month': u'Enter a valid month.',
        'invalid_year': u'Enter a valid year.',
    }

    def __init__(self, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        fields = (
            forms.ChoiceField(choices=self.EXP_MONTH,
                              error_messages={'invalid': errors['invalid_month']}),
            forms.ChoiceField(choices=self.EXP_YEAR,
                              error_messages={'invalid': errors['invalid_year']}),
        )
        super(CCExpField, self).__init__(fields, *args, **kwargs)
        self.widget = CCExpWidget(widgets=[fields[0].widget, fields[1].widget])

    def clean(self, value):
        exp = super(CCExpField, self).clean(value)
        if date.today() > exp:
            raise forms.ValidationError("The expiration date you entered is in the past.")

        return exp

    def compress(self, data_list):
        if data_list:
            if data_list[1] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_year']
                raise forms.ValidationError(error)
            if data_list[0] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_month']
                raise forms.ValidationError(error)
            year = int(data_list[1])
            month = int(data_list[0])
            # find last day of the month
            day = monthrange(year, month)[1]
            return date(year, month, day)
        return None


class BillingInfoForm(forms.Form):
    billing_name = forms.CharField(label="Name", required=False, max_length=40,
                                   widget=forms.TextInput(attrs={'class': 'srm-input'}))

    address_line1 = forms.CharField(label="Address Line 1", required=False, max_length=100,
                                    widget=forms.TextInput(attrs={'class': 'srm-input'}))

    address_line2 = forms.CharField(label="Address Line 2", required=False, max_length=100,
                                    widget=forms.TextInput(attrs={'class': 'srm-input'}))

    address_city = forms.CharField(label="City", required=False, max_length=100,
                                   widget=forms.TextInput(attrs={'class': 'srm-input'}))

    address_state = forms.CharField(label="State", required=False, max_length=100,
                                    widget=forms.TextInput(attrs={'class': 'srm-input'}))

    address_zip = forms.CharField(label="Zip", required=False, max_length=10,
                                  widget=forms.TextInput(attrs={'class': 'srm-input'}))

    address_country = forms.CharField(label="Country", required=False, max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'srm-input'}))

    def __init__(self, *args, **kwargs):
        super(BillingInfoForm, self).__init__(*args, **kwargs)
        # self.fields['billing_name'].widget.attrs['data-stripe'] = 'name'
        self.fields['address_line1'].widget.attrs['data-stripe'] = 'address_line1'
        self.fields['address_line2'].widget.attrs['data-stripe'] = 'address_line2'
        self.fields['address_city'].widget.attrs['data-stripe'] = 'address_city'
        self.fields['address_state'].widget.attrs['data-stripe'] = 'address_state'
        self.fields['address_zip'].widget.attrs['data-stripe'] = 'address_zip'
        self.fields['address_country'].widget.attrs['data-stripe'] = 'address_country'


class CreditCardForm(forms.Form):
    fullname = forms.CharField(label="Cardholder Name", required=True,
                               widget=forms.TextInput(attrs={'class': 'srm-input'}))
    card_number = CreditCardField(label="Card Number", required=True,
                                  widget=forms.TextInput(attrs={'class': 'srm-input'}))
    expiration = CCExpField(label="Card Expiry MMYY", required=True,
                            widget=forms.Select(attrs={'class': 'srm-input'}))

    cvc = forms.IntegerField(label="Card CVV", required=True, max_value=9999,
                             widget=forms.TextInput(attrs={
                                 'maxlength': '4', 'class': 'srm-input'}))

    stripeToken = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(CreditCardForm, self).__init__(*args, **kwargs)
        self.fields['fullname'].widget.attrs['data-stripe'] = 'name'
        self.fields['card_number'].widget.attrs['data-stripe'] = 'number'
        self.fields['cvc'].widget.attrs['data-stripe'] = 'cvc'
        self.fields['expiration'].widget.widgets[0].attrs['data-stripe'] = 'exp_month'
        self.fields['expiration'].widget.widgets[1].attrs['data-stripe'] = 'exp_year'

    def clean(self):
        """
        The clean method will effectively charge the card and create a new
        Sale instance. If it fails, it simply raises the error given from
        Stripe's library as a standard ValidationError for proper feedback.
        """
        cleaned = super(CreditCardForm, self).clean()

        if not self.errors:
            number = self.cleaned_data["card_number"]
            fullname = self.cleaned_data["fullname"]
            exp_month = self.cleaned_data["expiration"].month
            exp_year = self.cleaned_data["expiration"].year
            cvc = self.cleaned_data["cvc"]

        return cleaned


class CreditCardAndBillingInfoForm(CreditCardForm, BillingInfoForm):
    """Credit Card and Billing info Form"""

    def save_customer(self, request):
        """ Get or create customer instance. (So, this represents
         a customer but into the billing model, not in the User model."""
        exists_customer = hasattr(request.user_profile, 'customer')

        if exists_customer:
            customer = request.user_profile.customer
            customer.billing_name = self.cleaned_data.get('billing_name', '')
            customer.save()
            return customer
        else:
            kwargs = {
                'user': request.user_profile,
                'email': request.user_profile.email,

                'billing_name': self.cleaned_data.get('billing_name', ''),
                'billing_address_1': self.cleaned_data.get('address_line1', ''),
                'billing_address_2': self.cleaned_data.get('address_line2', ''),
                'billing_city': self.cleaned_data.get('address_city', ''),
                'billing_state': self.cleaned_data.get('address_state', ''),
                'billing_zip': self.cleaned_data.get('address_zip', ''),
                'billing_country': self.cleaned_data.get('address_country', ''),
            }
            return Customer.objects.create(**kwargs)


class RedirectNumberCreateForm(forms.ModelForm):
    from_no = forms.ModelChoiceField(queryset=TwilioNumber.objects.none())  # for security purposes

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RedirectNumberCreateForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['from_no'].queryset = TwilioNumber.objects.filter(
                user=user, is_redirected=False)

    class Meta:
        model = RedirectNumber
        fields = ('from_no', 'to_no')

    def validNumber(self, phone_nuber):
        pattern = re.compile("^\+(?:[0-9]?){6,14}[0-9]$", re.IGNORECASE)
        return pattern.match(phone_nuber) is not None

    def clean_to_no(self):
        if self.validNumber(self.cleaned_data['to_no']):
            return self.cleaned_data['to_no']
        raise ValidationError('Enter valid phone number.')


class PackageForm(forms.Form):
    package = forms.ModelChoiceField(PackageType.objects.all())

    def clean(self):
        cleaned_data = super(PackageForm, self).clean()
        numbers = self.data.getlist('numbers')
        if not numbers:
            raise forms.ValidationError('Choose at least one number')

        cleaned_data['numbers'] = numbers
        return cleaned_data


class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(PasswordForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not check_password(password, self.user.password):
            raise forms.ValidationError('Invalid password')
        return password


class ChangeCardForm(forms.Form):
    fullname = forms.CharField(label="Cardholder Name", required=True,
                               widget=forms.TextInput(attrs={'class': 'srm-input'}))
    exp_month = forms.CharField(label="Expiration Month", required=True,
                                widget=forms.TextInput(attrs={'class': 'srm-input'}))
    exp_year = forms.CharField(label="Expiration Year", required=True,
                               widget=forms.TextInput(attrs={'class': 'srm-input'}))

    def clean(self):
        cleaned_data = super(ChangeCardForm, self).clean()
        fullname = cleaned_data.get('fullname')
        exp_month = cleaned_data.get('exp_month')
        exp_year = cleaned_data.get('exp_year')
        return cleaned_data
