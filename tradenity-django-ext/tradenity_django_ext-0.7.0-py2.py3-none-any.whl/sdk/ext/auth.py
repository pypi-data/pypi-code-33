from tradenity.token_holder import AuthTokenHolder
from tradenity_django.sdk.ext.middleware import CurrentRequestMiddleware


class DjangoAuthTokenHolder(AuthTokenHolder):
    AUTH_TOKEN_NAME = 'tradenity_auth_token'

    def __init__(self):
        super(DjangoAuthTokenHolder, self).__init__()
        self._token = None

    @property
    def token(self):
        session = CurrentRequestMiddleware.get_request().session
        return session.get(self.AUTH_TOKEN_NAME, None)

    @token.setter
    def token(self, value):
        session = CurrentRequestMiddleware.get_request().session
        session[self.AUTH_TOKEN_NAME] = value

    def reset(self):
        session = CurrentRequestMiddleware.get_request().session
        del session[self.AUTH_TOKEN_NAME]
