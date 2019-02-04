from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin

from ..form_validators import AeSusarFormValidator
from ..models import AeSusar
from .modelform_mixin import ModelFormMixin


class AeSusarForm(
    FormValidatorMixin, ModelFormMixin, ActionItemFormMixin, forms.ModelForm
):

    form_validator_cls = AeSusarFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = AeSusar
        fields = "__all__"
