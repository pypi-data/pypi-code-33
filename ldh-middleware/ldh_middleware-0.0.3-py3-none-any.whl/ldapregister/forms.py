from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm as BaseRegistrationForm

User = get_user_model()


class AuthenticationForm(BaseAuthenticationForm):
    # this currently has no effect

    def __init__(self, request=None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(request, *args, **kwargs)
        self.fields["password"].label = _("Passphrase")


class RegistrationForm(BaseRegistrationForm):

    email = None  # override base definition to remove email field

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields[User.USERNAME_FIELD].label = _("Username")
        self.fields["password1"].label = _("Passphrase")
        self.fields["password2"].label = _("Passphrase confirmation")
        self.fields["password2"].help_text = _("Enter the same passphrase as before, for verification.")

    class Meta(BaseRegistrationForm.Meta):

        model = User

        # override base definition to remove email field
        fields = (
            User.USERNAME_FIELD,
            'password1',
            'password2',
        )
