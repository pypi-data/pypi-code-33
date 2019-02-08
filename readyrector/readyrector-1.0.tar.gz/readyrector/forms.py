from urllib.parse import urlparse

from django import forms
from django.utils.translation import gettext_lazy as _

from . import models


class RedirectForm(forms.ModelForm):
    error_messages = {
        'invalid_path': _('This is not a valid path.'),
        'not_unique': _('This path is already used.'),
    }

    class Meta:
        model = models.Redirect
        fields = ('from_path', 'to_url')

    def clean_from_path(self):
        path = self.cleaned_data.get('from_path', '').lstrip('/')
        parsed_path = urlparse(path).path.strip()
        if not parsed_path:
            raise forms.ValidationError(
                self.error_messages['invalid_path'], 'invalid')

        qs = models.Redirect.objects.filter(from_path__iexact=parsed_path)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                self.error_messages['not_unique'],
                code='from_path_not_unique')
        return parsed_path

    def save(self, commit=True):
        instance = super().save(commit=False)

        if 'from_path' in self.changed_data:
            instance.hits = 0
            instance.last_hit = None

        if commit:
            instance.save()
        return instance
