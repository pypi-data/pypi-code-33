from ambition_ae.models.ae_followup import AeFollowup
from django import forms
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin

from ..form_validators import AeInitialFormValidator
from ..models import AeInitial
from .modelform_mixin import ModelFormMixin


class AeInitialForm(
    FormValidatorMixin, ModelFormMixin, ActionItemFormMixin, forms.ModelForm
):

    form_validator_cls = AeInitialFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        if AeFollowup.objects.filter(ae_initial=self.instance.pk).exists():
            url = reverse("ambition_ae_admin:ambition_ae_aefollowup_changelist")
            url = f"{url}?q={self.instance.action_identifier}"
            raise forms.ValidationError(
                mark_safe(
                    "Unable to save. Follow-up reports exist. Provide updates "
                    "to this report using the AE Follow-up Report instead. "
                    f'See <A href="{url}">AE Follow-ups for {self.instance}</A>.'
                )
            )
        return cleaned_data

    class Meta:
        model = AeInitial
        fields = "__all__"
