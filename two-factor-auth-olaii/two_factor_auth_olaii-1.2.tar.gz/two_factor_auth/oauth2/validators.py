from __future__ import absolute_import, unicode_literals

from oauth2_provider.oauth2_validators import OAuth2Validator

from django.contrib.auth import authenticate
from django.utils.encoding import force_text

from two_factor_auth import strings
from two_factor_auth.models import Totp
from two_factor_auth.oauth2.exceptions import InvalidLoginError


class TwoFactorAuthOAuth2Validator(OAuth2Validator):
    """
    class::MFAOAuth2Validator()

    OAuth2 validator class for MFA that validates requests to authenticate
    with username and password by also verifying that they supply the correct
    MFA code or backup code if multifactor authentication is enabled.
    """

    def validate_user(
            self, username, password, client, request, *args, **kwargs):
        """
        Overrides the OAuth2Validator validate method to implement multi factor
        authentication.

        If MFA is disabled, authentication requires just a username and
        password.

        If MFA is enabled, authentication requires a username, password,
        and either a MFA code or a backup code. If the request only provides
        the username and password, the server will generate an appropriate
        challenge and respond with `mfa_required = True`.

        Upon using a backup code to authenticate, MFA will be disabled.

        :param attrs: Dictionary of data inputted by the user.
        :raises deux.oauth2.exceptions.InvalidLoginError: If invalid MFA
            code or backup code are submitted. Also if both types of code are
            submitted simultaneously.
        :raises deux.oauth2.exceptions.ChallengeRequiredMessage: If the user
            has MFA enabled but only supplies the correct username and
            password. This exception will prompt the OAuth2 system to send a
            response asking the user to supply an MFA code.
        """

        user = authenticate(username=username, password=password)
        if not (user and user.is_active):
            raise InvalidLoginError(force_text(
                strings.INVALID_CREDENTIALS_ERROR))

        twoFA = None
        totp = Totp.objects.devices_for_user(user)
        if totp.count() == 1:
            twoFA = totp[0]

        if twoFA and twoFA.enabled:
            twoFA_code = request.extra_credentials.get("twoFA_code")
            backup_code = request.extra_credentials.get("backup_code")

            if twoFA_code and backup_code:
                raise InvalidLoginError(force_text(strings.BOTH_CODES_ERROR))
            elif twoFA_code:
                if not twoFA.verify_token(twoFA_code):
                    raise InvalidLoginError(force_text(strings.INVALID_MFA_CODE_ERROR))
            elif backup_code:
                if not twoFA.check_and_use_backup_code(backup_code):
                    raise InvalidLoginError(force_text(strings.INVALID_BACKUP_CODE_ERROR))
            else:
                raise InvalidLoginError(force_text(strings.TWO_FACTOR_AUTH_REQUIRED))
        request.user = user
        return True
