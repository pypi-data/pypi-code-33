from collections import OrderedDict

from directory_client_core.base import AbstractAPIClient
from directory_client_core.authentication import AuthenticatorNegotiator

from directory_sso_api_client.version import __version__


class UserAPIClient(AbstractAPIClient):

    endpoints = {
        'session_user': 'api/v1/session-user/',
        'oauth2_user_profile': 'oauth2/user-profile/v1/',
        'last_login': 'api/v1/last-login/',
        'check_password': 'api/v1/password-check/',
        'verification': 'api/v1/verification-code/',
        'verify_verification': 'api/v1/verification-code/verify/',
        'user_create': 'api/v1/user/',
        'user_create_profile': 'api/v1/user/profile/',
    }
    version = __version__

    def get_session_user(self, session_id):
        return self.get(
            url=self.endpoints['session_user'],
            params={'session_key': session_id}
        )

    def get_oauth2_user_profile(self, bearer_token):
        return self.get(
            url=self.endpoints['oauth2_user_profile'],
            authenticator=AuthenticatorNegotiator(bearer_token=bearer_token)
        )

    def create_verification_code(self, sso_session_id):
        authenticator = AuthenticatorNegotiator(
            sso_session_id=sso_session_id,
        )
        return self.post(
            url=self.endpoints['verification'],
            authenticator=authenticator
        )

    def verify_verification_code(self, sso_session_id, code):
        authenticator = AuthenticatorNegotiator(sso_session_id=sso_session_id)
        return self.post(
            url=self.endpoints['verify_verification'],
            data={"code": code},
            authenticator=authenticator
        )

    def check_password(self, session_id, password):
        url = self.endpoints['check_password']
        data = OrderedDict(
            [('session_key', session_id), ('password', password)]
        )
        return self.post(url, data)

    def get_last_login(self, start=None, end=None):
        params = {}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        params = params or None

        return self.get(
            url=self.endpoints['last_login'],
            params=params
        )

    def create_user(self, email, password):
        url = self.endpoints['user_create']
        data = OrderedDict(
            [('email', email), ('password', password)]
        )
        return self.post(url, data)

    def create_user_profile(self, sso_session_id, data):
        authenticator = AuthenticatorNegotiator(sso_session_id=sso_session_id)
        url = self.endpoints['user_create_profile']
        return self.post(url, data, authenticator=authenticator)
