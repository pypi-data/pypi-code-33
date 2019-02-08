from django.conf import settings
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from generic.helpers import get_current_datetime


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:
    Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from authentication.models import AuthToken
        return AuthToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        model = self.get_model()
        model.objects.filter(created__lte=get_current_datetime()
                             - settings.REFRESH_TOKEN_EXPIRY).delete()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token, request)

    def authenticate_credentials(self, key, request):
        model = self.get_model()

        exp = settings.TOKEN_EXPIRY
        token_name = 'token'

        if 'refresh' in request.META['PATH_INFO']:
            exp = settings.REFRESH_TOKEN_EXPIRY
            token_name = 'refresh token'

        try:
            unsigned_token = signing.loads(key, max_age=exp, salt='access_token')
            token_id = unsigned_token['token_id']
            user = model.objects.get(id=token_id).user
        except signing.SignatureExpired:
            raise exceptions.AuthenticationFailed("Expired {0}.".format(token_name))
        except signing.BadSignature:
            raise exceptions.AuthenticationFailed("Invalid {0}.".format(token_name))
        except ObjectDoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid {0}.".format(token_name))

        return user, key

    def authenticate_header(self, request):
        return self.keyword
