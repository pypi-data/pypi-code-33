import json

from django.conf import settings

from captcha._compat import (
    build_opener, ProxyHandler, PY2, Request, urlencode, urlopen
)
from captcha.constants import DEFAULT_RECAPTCHA_DOMAIN
from captcha.decorators import generic_deprecation


RECAPTCHA_SUPPORTED_LANUAGES = ("en", "nl", "fr", "de", "pt", "ru", "es", "tr")


class RecaptchaResponse(object):
    def __init__(self, is_valid, error_codes=None):
        self.is_valid = is_valid
        self.error_codes = error_codes or []


def recaptcha_request(params):
    request_object = Request(
        url="https://%s/recaptcha/api/siteverify" % getattr(
            settings, "RECAPTCHA_DOMAIN", DEFAULT_RECAPTCHA_DOMAIN
        ),
        data=params,
        headers={
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "reCAPTCHA Django"
        }
    )

    # Add proxy values to opener if needed.
    opener_args = []
    proxies = getattr(settings, "RECAPTCHA_PROXY", {})
    if proxies:
        opener_args = [ProxyHandler(proxies)]
    opener = build_opener(*opener_args)

    # Get response from POST to Google endpoint.
    return opener.open(
        request_object,
        timeout=getattr(settings, "RECAPTCHA_VERIFY_REQUEST_TIMEOUT", 10)
    )


def submit(recaptcha_response, private_key, remoteip):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    recaptcha_response -- The value of reCAPTCHA response from the form
    private_key -- your reCAPTCHA private key
    remoteip -- the user's ip address
    """
    params = urlencode({
        "secret": private_key,
        "response": recaptcha_response,
        "remoteip": remoteip,
    })

    if not PY2:
        params = params.encode("utf-8")

    response = recaptcha_request(params)
    data = json.loads(response.read().decode("utf-8"))
    response.close()
    return RecaptchaResponse(
        is_valid=data["success"],
        error_codes=data.get("error-codes")
    )
