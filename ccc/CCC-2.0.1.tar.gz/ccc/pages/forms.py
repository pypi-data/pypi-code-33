from django import forms


class ContactUsForm(forms.Form):
    """Contact us form
    """
    contact_email = forms.EmailField(required=True)
    content = forms.CharField(
        required=True,
        widget=forms.Textarea
    )
