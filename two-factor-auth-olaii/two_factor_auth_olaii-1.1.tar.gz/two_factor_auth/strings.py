from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

#: Error if user submits both MFA and backup code for authentication.
BOTH_CODES_ERROR = _(
    "Login does not take both a verification and backup code.")

#: Error if MFA is unexpectedly in a disabled state.
DISABLED_ERROR = _("Two factor authentication is not enabled.")

#: Error if MFA is unexpectedly in an enabled state.
ENABLED_ERROR = _("Two factor authentication is already enabled.")

#: Error if an invalid backup code is entered.
INVALID_BACKUP_CODE_ERROR = _("Please enter a valid backup code.")

#: Error if a user provides an invalid username/password combination.
INVALID_CREDENTIALS_ERROR = _("Unable to log in with provided credentials.")

#: Error if an invalid MFA code is entered.
INVALID_MFA_CODE_ERROR = _("Please enter a valid code.")

TWO_FACTOR_AUTH_REQUIRED = _("Two factor authentication is required.")
