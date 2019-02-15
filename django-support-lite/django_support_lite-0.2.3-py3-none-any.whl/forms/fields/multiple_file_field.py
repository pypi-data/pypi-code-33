from django import forms
from django.forms import ValidationError


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.min_count = kwargs.pop("min_count", None)
        self.max_count = kwargs.pop("max_count", None)

        super(MultipleFileField, self).__init__(*args, **kwargs)

    def clean(self, value, initial=None):
        files_count = len(value)

        if not self.required and files_count == 0:
            return []

        if self.min_count and files_count < self.min_count:
            raise ValidationError(
                "Необходимо указать не менее {} файлов, указано {}.".format(self.min_count, files_count)
            )

        if self.max_count and files_count > self.max_count:
            # TODO: i18n
            raise ValidationError(
                "Необходимо указать не более {} файлов, указано {}.".format(self.max_count, files_count)
            )

        for file in value:
            self.run_validators(file)

        return value
