from __future__ import absolute_import, unicode_literals

from oauth2_provider.views import TokenView

from two_factor_auth.oauth2.backends import TwoFactorAuthRequestBackend
from two_factor_auth.oauth2.validators import TwoFactorAuthOAuth2Validator


class TwoFactorAuthTokenView(TokenView):
    """
    class::MFATokenView()

    Extends OAuth's base TokenView to support MFA.
    """

    #: Use Deux's custom backend for the MFA OAuth api.
    oauthlib_backend_class = TwoFactorAuthRequestBackend

    #: Use Deux's custom validator for the MFA OAuth api.
    validator_class = TwoFactorAuthOAuth2Validator
