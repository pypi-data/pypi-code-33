import logging
import uuid

import requests

from paymentsos.authorizations import Authorization
from paymentsos.captures import Capture
from paymentsos.charges import Charge
from paymentsos.credits import Credit
from paymentsos.customers import Customer
from paymentsos.payment_methods import PaymentMethod
from paymentsos.payments import Payment
from paymentsos.redirections import Redirection
from paymentsos.refunds import Refund
from paymentsos.tokens import Token
from paymentsos.voids import Void

try:
    from django_requests_logger.callbacks import logger as django_requests_logger

    is_django_requests_logger_installed = True
except:
    is_django_requests_logger_installed = False

fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)


class Client(object):
    URL_BASE = 'https://api.paymentsos.com'

    def __init__(self, app_id, public_key, private_key, api_version='1.2.0', test=False, debug=False,
                 requests_logger=False):
        self.app_id = app_id
        self.public_key = public_key
        self.private_key = private_key
        self.api_version = api_version
        self.test = test
        self.debug = debug
        self.requests_logger = requests_logger

        self.authorizations = Authorization(self)
        self.captures = Capture(self)
        self.charges = Charge(self)
        self.credits = Credit(self)
        self.customers = Customer(self)
        self.payment_methods = PaymentMethod(self)
        self.payments = Payment(self)
        self.redirections = Redirection(self)
        self.refunds = Refund(self)
        self.tokens = Token(self)
        self.voids = Void(self)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    @property
    def is_test(self):
        return self.test

    @property
    def is_debug(self):
        return self.debug

    def _get(self, url, **kwargs):
        return self._request('GET', url, **kwargs)

    def _post(self, url, **kwargs):
        return self._request('POST', url, **kwargs)

    def _put(self, url, **kwargs):
        return self._request('PUT', url, **kwargs)

    def _delete(self, url, **kwargs):
        return self._request('DELETE', url, **kwargs)

    def _request(self, method, url, headers=None, **kwargs):
        _headers = {
            'api-version': self.api_version,
            'x-payments-os-env': 'test' if self.test else 'live',
            'idempotency_key': uuid.uuid4().hex,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if headers:
            _headers.update(headers)

        # Do not send None values
        if 'json' in kwargs:
            kwargs['json'] = {k: v for k, v in kwargs['json'].items() if v is not None}

        if self.is_debug:
            self.logger.debug('{} {} {} {}'.format(method, url, headers, kwargs))

        if self.requests_logger:
            if is_django_requests_logger_installed:
                kwargs['hooks'] = {'response': django_requests_logger}
            else:
                raise Exception('django_requests_logger is not installed')
        return self._parse(requests.request(method, url, headers=_headers, timeout=60, **kwargs))

    def _parse(self, response):
        status_code = response.status_code
        content_type = response.headers.get('Content-Type', None)
        request_id = response.headers.get('x-zooz-request-id', None)
        if content_type and 'application/json' in content_type:
            r = response.json()
        else:
            if self.is_debug:
                fmt = 'The response with status code ({}) and request id ({}) is not JSON deserializable. Response: {}'
                self.logger.warning(fmt.format(status_code, request_id, response.text))

            return response.text

        return r

    def _get_public_headers(self):
        headers = {
            'public_key': self.public_key,
        }
        return headers

    def _get_private_headers(self):
        headers = {
            'app_id': self.app_id,
            'private_key': self.private_key,
        }
        return headers
