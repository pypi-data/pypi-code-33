from django import forms

# place form definition here


class DocumentForm(forms.Form):
    document = forms.ImageField()
