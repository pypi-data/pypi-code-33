# Import models

from django import forms
from django.conf import settings
from phonenumber_field.validators import validate_international_phonenumber


class FormInviteMember(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'srm-input'}))
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'srm-input'}))
    email = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'srm-input'}))

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        validate_international_phonenumber(phone)
        return phone

    def add_member(self, team):
        """Add member and automatically send Invitation..."""
        team.add_member(
            name=self.cleaned_data['name'], email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone_number']
        )
