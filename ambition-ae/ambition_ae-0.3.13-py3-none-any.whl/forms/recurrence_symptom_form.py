from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin

from ..form_validators import RecurrenceSymptomFormValidator
from ..models import RecurrenceSymptom
from .modelform_mixin import ModelFormMixin


class RecurrenceSymptomForm(
    FormValidatorMixin, ModelFormMixin, ActionItemFormMixin, forms.ModelForm
):

    form_validator_cls = RecurrenceSymptomFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = RecurrenceSymptom
        fields = "__all__"
