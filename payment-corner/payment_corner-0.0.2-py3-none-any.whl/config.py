import requests
from paymentcorner.auth import Auth


class Config(object):
    _token = None

    ENV_PROD = 'prod'
    ENV_SANDBOX = 'sandbox'

    ENV_URLS = {
        ENV_PROD: 'http://productionapi.paymentcorner.com/',
        ENV_SANDBOX: 'http://sandboxapi.paymentcorner.com/',
    }

    ENDPOINT_URLS = {
        'login': 'login',
        'logout': 'logout',
        'fx_transaction': 'fx-transaction',
        'retrieve_fx_transaction': 'retrieve-fx-transaction',
        'retrieve_fx_transaction_record': 'retrieve-fx-transaction-record',
        'change_fx_conversion_value_date': 'change-fx-conversion-value-date',
        'change_fx_conversion_delivery_date_quotation': 'change-fx-conversion-delivery-date-quotation',
        'fx_market_rate_with_mark_up': 'fx-market-rate-w/mark-up',
        'fx_market_rate': 'fx-market-rate'
    }

    def __init__(self, email, password, env='demo'):
        self.email = email
        self.password = password
        self.env = env
        self.session = requests.Session()
        super(Config, self).__init__()

    @property
    def token(self):
        if self._token is None:
            if self.email is None:
                raise RuntimeError('Invalid email')
            if self.password is None:
                raise RuntimeError('Invalid password')
            self._token = Auth(self).authenticate()['result']['auth_token']

        return self._token

    def environment_url(self):
        if self.env not in self.ENV_URLS:
            raise RuntimeError('%s is not a valid environment' % self.env)

        return self.ENV_URLS[self.env]
