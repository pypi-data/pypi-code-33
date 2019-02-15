from django import forms
from django.utils.datastructures import MultiValueDict


class MultipleFileInput(forms.ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        attrs["multiple"] = "multiple"

        return super(MultipleFileInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if isinstance(files, MultiValueDict):
            return files.getlist(name)

        return []
