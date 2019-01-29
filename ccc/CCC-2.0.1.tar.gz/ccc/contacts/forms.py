import os

from django import forms

from ccc.campaigns.models import Campaign
from ccc.contacts.lead_importer import clean_phone
from ccc.contacts.models import Contact, ContactCheckin, ContactGroup


class ContactCheckinForm(forms.ModelForm):
    schedular_step = forms.ChoiceField(choices=(
        ('0', 'Immediately'),
        ('86400', 'Day'),
        ('3600', 'Hour'),
        ('60', 'Minute'),
    ))

    class Meta:
        model = ContactCheckin
        fields = ['contact', 'campaign', 'sms', 'delay', 'schedular_step']

    def __init__(self, *args, **kwargs):
        super(ContactCheckinForm, self).__init__(*args, **kwargs)
        self.fields['campaign'].empty_label = None
        self.fields['contact'].widget = forms.HiddenInput()

    def clean(self):
        """
        Contactk checking form. Clean method,
        :return:
        """
        cleaned_data = super(ContactCheckinForm, self).clean()

        from ccc.survey.models import Question
        delay, schedular_step = cleaned_data['delay'], cleaned_data['schedular_step']
        cleaned_data['delay'] = Question.clean_delay_value(delay, schedular_step)

        return cleaned_data


class CampaignAndGroupMixin(object):
    """ Form form Creating Contacts, with an additional campaign field. """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CampaignAndGroupMixin, self).__init__(*args, **kwargs)

        if self.user:
            # Add `campaigns` and `groups` fields
            # filter queryset for security purposes and order by lowercase name
            self.fields['campaigns'] = forms.ModelMultipleChoiceField(
                required=False,
                queryset=Campaign.objects
                    .filter(user=self.user, active=True)
                    .extra(select={'lower_name': 'lower(name)'})
                    .order_by('lower_name'))

            self.fields['groups'] = forms.ModelMultipleChoiceField(
                required=False,
                queryset=ContactGroup.objects
                    .filter(user=self.user)
                    .extra(select={'lower_name': 'lower(name)'})
                    .order_by('lower_name'))


class ContactFormBase(forms.ModelForm):
    """ Form form Creating and updating Contacts """

    first_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': 'First name e.g. John'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Last name e.g. Doe'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={'placeholder': 'me@mydomain.com'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Format  +446567898765'}))

    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if phone:
            phone, country = clean_phone(phone)
            if phone is None:
                raise forms.ValidationError("Invalid phone number.")

        return phone

    def clean(self):
        cleaned_data = super(ContactFormBase, self).clean()
        if not cleaned_data.get('phone') and not cleaned_data.get('email'):
            msg = "Either email or phone is required"
            self._errors["phone"] = self.error_class([msg])
            self._errors["email"] = self.error_class([msg])

        return cleaned_data


class ContactForm(ContactFormBase):
    note = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Notes'}))

    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'company_name', 'email', 'phone', 'note')


class ContactSignupForm(ContactFormBase):
    def __init__(self, *args, **kwargs):
        self.campaign = kwargs.pop('campaign', None)
        super(ContactSignupForm, self).__init__(*args, **kwargs)

        if not self.campaign.embed_form_last_name:
            del self.fields['last_name']

        if not self.campaign.embed_form_email:
            del self.fields['email']

        if not self.campaign.embed_form_phone:
            del self.fields['phone']

        for extra_field in self.campaign.signup_extra_fields.all():
            self.fields['property_%s' % extra_field.pk] = forms.CharField(
                label=extra_field.name, initial='', required=False)

    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'email', 'phone')

    def clean(self):
        cleaned_data = super(ContactFormBase, self).clean()

        if self.campaign.embed_form_email and self.campaign.embed_form_phone:
            if not cleaned_data.get('phone') and not cleaned_data.get('email') \
                and "phone" not in self._errors \
                and "email" not in self._errors:
                msg = "Either email or phone is required"
                self._errors["phone"] = self.error_class([msg])
                self._errors["email"] = self.error_class([msg])

        if self.campaign.embed_form_email and not self.campaign.embed_form_phone:
            if not cleaned_data.get('email') and "email" not in self._errors:
                self._errors["email"] = self.error_class(['This field is required'])

        if not self.campaign.embed_form_email and self.campaign.embed_form_phone:
            if not cleaned_data.get('phone') and "phone" not in self._errors:
                self._errors["phone"] = self.error_class(['This field is required'])

        return cleaned_data


class CreateEditContactForm(CampaignAndGroupMixin, ContactForm):
    pass


class UploadContactForm(CampaignAndGroupMixin, forms.Form):
    excel = forms.FileField()

    def clean_excel(self):
        excel = self.cleaned_data['excel']

        extension = os.path.splitext(excel.name)[1]
        if not extension.lower() in ['.xls', '.xlsx']:
            raise forms.ValidationError("Only Excel XLS and XLSX files are supported")

        return excel


class ImportContactForm(CampaignAndGroupMixin, forms.Form):
    pass


class AddContactsToCampaignForm(CampaignAndGroupMixin, forms.Form):
    campaign_to_add = forms.ModelChoiceField(Campaign.objects.none())
    contacts = forms.ModelMultipleChoiceField(Contact.objects.none())

    def __init__(self, *args, **kwargs):
        # TODO: refactor this:
        # CampaignAndGroupMixin ancestor is not needed, but
        # upon removing that, it is essential to pop the 'user from the kwargs here
        super(AddContactsToCampaignForm, self).__init__(*args, **kwargs)
        if self.user:
            # filter queryset for security purposes
            self.fields['campaign_to_add'].queryset = Campaign.objects \
                .filter(user=self.user, active=True)
            self.fields['contacts'].queryset = Contact.objects \
                .filter(user=self.user)


class AddContactsToGroupForm(CampaignAndGroupMixin, forms.Form):
    group_to_add = forms.ModelChoiceField(ContactGroup.objects.none())
    contacts = forms.ModelMultipleChoiceField(Contact.objects.none())

    def __init__(self, *args, **kwargs):
        # TODO: refactor this:
        # CampaignAndGroupMixin ancestor is not needed, but
        # upon removing that, it is essential to pop the 'user from the kwargs here
        super(AddContactsToGroupForm, self).__init__(*args, **kwargs)
        if self.user:
            # filter queryset for security purposes
            self.fields['group_to_add'].queryset = ContactGroup.objects \
                .filter(user=self.user)
            self.fields['contacts'].queryset = Contact.objects \
                .filter(user=self.user)


class CreateContactGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateContactGroupForm, self).__init__(*args, **kwargs)
        self.fields['user'].required = False

    def clean_user(self):
        return self.user

    class Meta:
        model = ContactGroup
        fields = ('user', 'name', 'contacts')
