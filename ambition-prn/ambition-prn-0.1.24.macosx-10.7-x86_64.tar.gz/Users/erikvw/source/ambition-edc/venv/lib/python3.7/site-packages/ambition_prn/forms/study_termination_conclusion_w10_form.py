from django import forms
from edc_base.sites.forms import SiteModelFormMixin
from edc_form_validators import FormValidatorMixin

from ..models import StudyTerminationConclusionW10
from ..form_validators import StudyTerminationConclusionW10FormValidator


class StudyTerminationConclusionW10Form(SiteModelFormMixin, FormValidatorMixin,
                                        forms.ModelForm):

    form_validator_cls = StudyTerminationConclusionW10FormValidator

    class Meta:
        model = StudyTerminationConclusionW10
        fields = '__all__'
        labels = {
            'offschedule_datetime': 'Date patient terminated on study:',
        }
