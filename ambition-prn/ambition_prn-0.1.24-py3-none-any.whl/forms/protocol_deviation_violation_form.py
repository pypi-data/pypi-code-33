from django import forms
from edc_base.sites.forms import SiteModelFormMixin
from edc_form_validators import FormValidatorMixin

from ..form_validators import ProtocolDeviationViolationFormValidator
from ..models import ProtocolDeviationViolation


class ProtocolDeviationViolationForm(SiteModelFormMixin, FormValidatorMixin,
                                     forms.ModelForm):

    form_validator_cls = ProtocolDeviationViolationFormValidator

    class Meta:
        model = ProtocolDeviationViolation
        fields = '__all__'
