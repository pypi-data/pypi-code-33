"""
    tupas_verisigner
    ~~~~~~~~~~~~

    TUPAS request URL verification and signing.

    :copyright: (c) 2019 by Adarsh Krishnan

    :license: MIT, see LICENSE for more details.
"""
from hashlib import sha256
from urllib.parse import parse_qs, urlencode, urlparse

__version__ = '0.0.1'


VERIFICATION_ARG_NAMES = (
    'B02K_VERS',
    'B02K_TIMESTMP',
    'B02K_IDNBR',
    'B02K_STAMP',
    'B02K_CUSTNAME',
    'B02K_KEYVERS',
    'B02K_ALG',
    'B02K_CUSTID',
    'B02K_CUSTTYPE',
)

INPUT_SIGNATURE_ARG_NAME = 'B02K_MAC'

CUSTOMER_NAME_ARG_NAME = 'B02K_CUSTNAME'


class TupasVerisigner(object):
    def __init__(
        self,
        input_secret,
        output_secret,
        base_output_url,
        error_url,
        encoding='Windows-1252'
    ):
        self.input_secret = input_secret
        self.output_secret = output_secret
        self.base_output_url = base_output_url
        self.error_url = error_url
        self.encoding = encoding

    def verify_and_sign_url(self, url):
        query_args = parse_qs(urlparse(url).query, encoding=self.encoding)
        if self._verify(query_args):
            return self._sign(query_args)
        return self.error_url

    def _verify(self, query_args):
        arg_values = []
        for arg in VERIFICATION_ARG_NAMES:
            arg_value = query_args.get(arg)
            if not arg_value or len(arg_value) == 0:
                return False
            arg_values.append(arg_value[0])
        signature_input_string = '&'.join(arg_values + [self.input_secret, ''])

        input_signature = query_args.get(INPUT_SIGNATURE_ARG_NAME)
        if not input_signature or len(input_signature) == 0:
            return False

        if not (
            self._get_sha256_hash(signature_input_string).lower() ==
            input_signature[0].lower()
        ):
            return False

        return True

    def _sign(self, query_args):
        firstname, lastname = [
            v.capitalize() for v in
            query_args[CUSTOMER_NAME_ARG_NAME][0].split(' ')
        ]
        output_hash = self._get_sha256_hash(
            'firstname={firstname}&lastname={lastname}#{output_secret}'.format(
                firstname=firstname,
                lastname=lastname,
                output_secret=self.output_secret,
            )
        )
        return '{base_url}/?{query_string}'.format(
            base_url=self.base_output_url,
            query_string=urlencode([
                ('firstname', firstname),
                ('lastname', lastname),
                ('hash', output_hash),
            ]),
            encoding=self.encoding,
        )

    def _get_sha256_hash(self, input_string):
        return sha256(bytes(input_string, encoding=self.encoding)).hexdigest()
