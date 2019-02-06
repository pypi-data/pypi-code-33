from flask import session

from tradenity.token_holder import AuthTokenHolder


class FlaskAuthTokenHolder(AuthTokenHolder):
    AUTH_TOKEN_NAME = 'tradenity_auth_token'

    def __init__(self):
        self._token = None

    @property
    def token(self):
        if self.AUTH_TOKEN_NAME in session:
            return session[self.AUTH_TOKEN_NAME]

    @token.setter
    def token(self, value):
        session[self.AUTH_TOKEN_NAME] = value

    def reset(self):
        del session[self.AUTH_TOKEN_NAME]

