import codecs
import hashlib
import hmac
import json
import uuid
import datetime
import logging
import re
import jwt
from requests.sessions import Session
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


logger = logging.getLogger(__name__)


class PunchhException(Exception):
    """Punchh related errors."""

    pass


class NoToken(AuthenticationFailed):
    default_detail = _('No token in request header.')
    default_code = 'jwt_missing'


class InvalidJWT(AuthenticationFailed):
    default_detail = _('Invalid JWT.')
    default_code = 'jwt_invalid'


class BadClaims(AuthenticationFailed):
    default_detail = _('Invalid Punchh JWT used.')
    default_code = 'jwt_claims_bad'


class BadPunchhToken(AuthenticationFailed):
    default_detail = _('Punchh servers rejected token.')
    default_code = 'punchh_token_invalid'


class PunchhSession(Session):
    """Creating our own Punchh session to perform our requests with the needed Punchh client signature header."""

    def __init__(self, base_url, secret, api_version='v1'):
        super().__init__()

        self.base_url = base_url
        self.secret = secret
        self.api_version = api_version

    def _generate_signature(self, url, r_body=None):
        uri = url.split(self.base_url)[1]
        encryption_type = hashlib.sha1
        if self.api_version == 'v2':
            encryption_type = hashlib.sha256

        if r_body:
            payload = uri + r_body
        else:
            payload = uri

        # Handling of hmac library for encryption of the header x-pch signature needed by Punchh
        new_hash = hmac.new(
            bytes(self.secret.encode('utf-8')),
            bytes(payload.encode('utf-8')),
            encryption_type).digest()

        signature = codecs.encode(new_hash, 'hex_codec')

        return signature

    def prepare_request(self, request):
        if request.data:
            request.data = json.dumps(request.data, separators=(',', ':'))
            sig = self._generate_signature(request.url, request.data)
        elif request.json:
            # TODO find out about why the json returns an invalid signature
            request.json = json.dumps(request.json, separators=(',', ':'))
            # sig = self._generate_signature(request.url, request.json)

        request.headers['Content-Type'] = 'application/json'
        request.headers['Accept'] = 'application/json'
        request.headers['x-pch-digest'] = sig

        return super().prepare_request(request)


def get_token(auth: dict, api_version: str = 'v1') -> str:
    """Get the appropriate token from an auth object."""
    # api token can only be 'v1' or 'v2'
    if api_version not in ['v1', 'v2']:
        raise PunchhException(f'Invalid api_version: {api_version}')

    try:
        return auth[f'{api_version}_token']
    except KeyError:
        raise PunchhException(f"Invalid Auth Token {api_version}.")


def create_jwt(data: dict, secret: str) -> str:
    """Create JWT that is compatible with `t3.drf.authentication.PunchhAuthentication`."""
    if not all([x in data for x in ['user_id', 'authentication_token', 'access_token']]):
        raise PunchhException('Invalid data used to generate token')

    claims = {
        'jti': str(uuid.uuid4()),
        'sub': data.get('user_id', None),
        'iat': datetime.datetime.utcnow(),
        'v1_token': data.get('authentication_token', None),
        'v2_token': data.get('access_token', None),
    }

    if not claims['sub'] or not claims['v1_token']:
        raise PunchhException('Data used to create JWT is incomplete.')

    if not claims['v2_token']:
        raise PunchhException('Data used to create JWT is incomplete.  Ensure that Punchh has turned on feature that '
                              'makes the `v1` login/register  calls return both the `authentication_token` (v1), as '
                              'well as the `authentication_token` (v2)')

    token = jwt.encode(
        claims,
        secret,
        algorithm='HS256',
    )

    return token.decode("utf-8")


class PunchhAuthentication(authentication.BaseAuthentication):
    """Django Rest Framework authentication class."""

    def authenticate(self, request):
        jwt_token = re.sub(f'^Bearer ', '', request.META.get('HTTP_AUTHORIZATION', ''))

        if not jwt_token:
            raise NoToken('No token in request header')

        try:
            payload = jwt.decode(jwt_token, settings.PUNCHH_CLIENT_SECRET, algorithms='HS256')
        except:
            raise InvalidJWT('Invalid JWT')

        # Verify that the token has the proper claims
        if not all([x in payload for x in ['jti', 'sub', 'iat', 'v1_token', 'v2_token']]):
            raise BadClaims('Invalid Punchh JWT used')

        user = payload['sub']
        v2_token = payload['v2_token']

        # If we want to verify that the auth tokens inside the JWT are valid,
        # then perform a retrieve user action.  We want to do this when we're
        # hitting endpoints that don't rely on Punchh's authentication system.
        # Doing this adds a round-trip request to Punchh's servers to EVERY call
        if settings.PUNCHH_AUTH_SERVER_VERIFY:
            # Make session for sending get request to punchh
            session = PunchhSession(
                settings.PUNCHH_V2_BASE_URL,
                settings.PUNCHH_CLIENT_SECRET,
                'v2',
            )

            # Send the request
            response = session.get(
                f'{settings.PUNCHH_V2_BASE_URL}/api2/mobile/users/{user}',
                data={'client': settings.PUNCHH_CLIENT_KEY},
                headers={'Authorization': f'Bearer {v2_token}'}
            )

            if response.status_code != 200:
                raise BadPunchhToken('Punchh servers rejected token')

        return (user, payload)
