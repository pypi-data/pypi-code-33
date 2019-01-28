# Plugin for cloudtoken.
# The SAML plugin must be loaded prior to this plugin. This plugin will use SAML credentials to generate a sign in URL.
# Input: Credentials
# Output: URL to stdout.

import argparse
from urllib.parse import urlencode

import requests


class Plugin(object):
    def __init__(self, config):
        self._name = 'url_generator'
        self._description = 'Generate a url from SAML credentials'
        self._config = config

    def __str__(self):
        return __file__

    @staticmethod
    def unset(args):
        pass

    @staticmethod
    def arguments(defaults):
        parser = argparse.ArgumentParser()
        parser.add_argument("-g",
                            "--generate-url",
                            dest="generate_url",
                            action="store_true",
                            help="Generate a sign in URL that can be used on the browser")
        parser.add_argument("--generate-url-duration",
                            default=43200,  # 12 hours
                            help="Duration of the temporary role to create for URL sign-in (in seconds). Must be less than the maximum session duration for the role.")
        parser.add_argument("--generate-url-suffix",
                            default=None,
                            help="Suffix to add to the destination URL. e.g. rds | cloudformation | sqs")
        return parser

    @staticmethod
    def generate_sign_in_url(credentials, destination_suffix, duration):
        """
        Generate a sign in URL from SAML credentials (assume_role_with_saml).
        Credentials must be a dictionary containing these keys:
        {
            'AccessKeyId': ...,
            'SecretAccessKey': ...,
            'sessionToken': ...,
            'Issuer': ...,
            ...
        }
        """
        if destination_suffix is None:
            destination_suffix = ''

        # boto does not support getSigninToken...yet
        sign_in_url = 'https://signin.aws.amazon.com/federation?'
        destination_url = 'https://console.aws.amazon.com/' + destination_suffix

        session_data = {
            "sessionId": credentials['AccessKeyId'],
            'sessionKey': credentials['SecretAccessKey'],
            'sessionToken': credentials['Token'],
        }

        sign_in_token_parameters = {
            'Action': 'getSigninToken',
            'SessionDuration': duration,
            'Session': session_data,
        }

        resp = requests.get(sign_in_url, params=urlencode(sign_in_token_parameters))
        resp.raise_for_status()

        sign_in_token = resp.json()['SigninToken']
        sign_in_params = {
            'Action': 'login',
            'Issuer': credentials['Issuer'],
            'SigninToken': sign_in_token,
            'Destination': destination_url,
        }

        return sign_in_url + urlencode(sign_in_params)

    def execute(self, data, args, flags):
        saml_plugin_output = next(
            filter(lambda plugin_payload: plugin_payload.get('plugin') == 'saml' and 'data' in plugin_payload, data),
            None
        )

        if saml_plugin_output is None:
            raise Exception("SAML credential response not found. Is the plugin loaded correctly?")

        sign_in_url = None
        if args.generate_url:
            sign_in_url = self.generate_sign_in_url(
                saml_plugin_output['data'], args.generate_url_suffix, args.generate_url_duration)
            print("Sign-In URL: {}".format(sign_in_url))

        data.append({'plugin': self._name, 'data': sign_in_url})
        return data
