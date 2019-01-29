from django import forms

from ccc.campaigns.models import Campaign
from ccc.template_design.models import TemplateDesign


class EmailTemplateDesignForm(forms.ModelForm):
    """Template Design Form"""
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'srm-input', 'placeholder': 'Template Name'}))

    class Meta:
        model = TemplateDesign
        fields = ('name', 'email_body', 'user', 'template_type', 'json_data')
        widgets = {'email_body': forms.HiddenInput(), 'user': forms.HiddenInput(),
                   'template_type': forms.HiddenInput(), 'json_data': forms.HiddenInput()}


class WebTemplateDesignForm(forms.ModelForm):
    """Template Design Form"""

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(WebTemplateDesignForm, self).__init__(*args, **kwargs)
        self.fields['campaign'].choices = Campaign.objects.filter(
            user=self.request.user, active=True).values_list('id', 'name')

    name = forms.CharField(label='Page Name',
                           widget=forms.TextInput(attrs={'class': 'srm-input', 'placeholder': 'Landing page Name', 'required':'required'}))
    campaign = forms.ChoiceField(choices=tuple(),
                                 label='Select Campaign',
                                 widget=forms.Select(attrs={'class': 'srm-input crm-select2', 'required':'required'}))

    class Meta:
        model = TemplateDesign
        fields = ('name', 'campaign', 'email_body', 'user', 'template_type', 'json_data')
        widgets = {'email_body': forms.HiddenInput(), 'user': forms.HiddenInput(),
                   'template_type': forms.HiddenInput(), 'json_data': forms.HiddenInput()}
