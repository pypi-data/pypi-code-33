import json

import phpass
from flask import current_app as app
from flask_jwt import _default_request_handler

from geokrety_api_models import User


def jwt_authenticate(username, password):
    """
    helper function to authenticate user if credentials are correct
    :param email:
    :param password:
    :return:
    """
    user = User.query.filter_by(name=username).first()
    if user is None:
        return None

    t_hasher = phpass.PasswordHash(11, False)

    auth_ok = t_hasher.check_password(
        password.encode('utf-8') + app.config['PASSWORD_HASH_SALT'],
        user.password.encode('utf-8')
    )

    if auth_ok:
        return user
    else:
        return None


def jwt_identity(payload):
    """
    Jwt helper function
    :param payload:
    :return:
    """
    return User.query.get(payload['identity'])


def get_identity():
    """
    To be used only if identity for expired tokens is required, otherwise use current_identity from flask_jwt
    :return:
    """
    token_second_segment = _default_request_handler().split('.')[1]
    missing_padding = len(token_second_segment) % 4

    # ensures the string is correctly padded to be a multiple of 4
    if missing_padding != 0:
        token_second_segment += b'=' * (4 - missing_padding)

    payload = json.loads(token_second_segment.decode('base64'))
    user = jwt_identity(payload)
    return user
