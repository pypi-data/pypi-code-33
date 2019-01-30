# -*- coding: utf-8 -*-

"""
This file implements features related to Authentication for the CloudCIX API.
"""

import requests

import cloudcix.api
import cloudcix.conf


def get_admin_token():
    """
    Generates an `admin` token using the credentials specified in the settings module
    (``CLOUDCIX_API_USERNAME``, ``CLOUDCIX_API_PASSWORD``, and ``CLOUDCIX_API_KEY``).
    """
    data = {
        'email': cloudcix.conf.settings.CLOUDCIX_API_USERNAME,
        'password': cloudcix.conf.settings.CLOUDCIX_API_PASSWORD,
        'api_key': cloudcix.conf.settings.CLOUDCIX_API_KEY,
    }
    response = cloudcix.api.Membership.token.create(data=data)
    if response.status_code == 201:
        return response.json()['token']
    raise Exception(response.json()['error_code'])


class TokenAuth(requests.auth.AuthBase):
    """
    Wrapper around :py:class:`requests.auth.AuthBase` that is designed to put a token into the correct header for use
    with our API.
    """

    def __init__(self, token):
        """
        Create an instance of the TokenAuth class with a specified token

        :param token: The token that will be used to authenticate the request.
        :type token: str
        """
        self.token = token

    def __call__(self, request):
        """
        Used to set the correct header in the request when the request is about to be sent.

        :param request: The request that this TokenAuth instance has been used for.
        :type request: requests.Request
        """
        request.headers['X-Auth-Token'] = self.token
        return request

    def __eq__(self, other):
        """
        Compares two instances of the TokenAuth class to check if they have the same token.

        :param other: Another instance of TokenAuth that will be compared against this one.
        :type other: cloudcix.auth.TokenAuth
        """
        return self.token == other.token
