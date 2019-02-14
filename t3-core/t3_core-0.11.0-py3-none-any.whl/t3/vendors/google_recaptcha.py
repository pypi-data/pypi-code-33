"""
This module will verify a user response token from google recaptcha.

In order to implement, you will need to include the site secret key in the
class constructor.

Standard recaptcha errors are returned in the JSON response from the Google API.

https://developers.google.com/recaptcha/docs/verify
"""

import logging
import requests

logger = logging.getLogger(__name__)


class ReCaptchaException(Exception):
    """Standard recaptcha exception."""

    pass


def verify(response, secret, remoteip=None):
    """
    Verify a front-end recaptcha response with google.

    response is the front-end recaptcha validation hash.
    secret is the key provided by the Google Recaptcha credentials.
    remoteip is the optional user's IP.
    """
    payload = {
        'response': response,
        'secret': secret,
    }

    if remoteip:
        payload['remoteip'] = remoteip

    res = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)

    if res.status_code != 200:
        raise ReCaptchaException

    return res
