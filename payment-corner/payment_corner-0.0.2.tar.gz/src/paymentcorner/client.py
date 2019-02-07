from paymentcorner.config import Config
from paymentcorner.http import Http
from paymentcorner.auth import Auth
from paymentcorner.error import *
from datetime import datetime


class Client(Http):
    _auth = None
    _client_id = None

    def __init__(self, email, password, client_id, env='sandbox'):
        config = Config(email, password, env)
        self._client_id = client_id
        super(Client, self).__init__(config)

    @staticmethod
    def validate_empty(data, required):
        for each in required:
            if each not in data or data[each] is None or data[each] == '':
                return False, each
        return True, ''

    @staticmethod
    def validate_currency(data, keys, length=3):
        for key in keys:
            if len(data[key]) != length or not data[key].isupper():
                return False, key
        return True, ''

    @staticmethod
    def validate_currency_amount(data, keys):
        for key in keys:
            if type(data[key]) not in [int, float] or data[key] <= 0:
                return False, key
        return True, ''

    def authenticate(self):
        if self._auth is None:
            self._auth = Auth(self.config)
        response = self._auth.authenticate()
        self.config._token = response['result']['auth_token']

    def fx_market_rate(self, data):
        data['client_id'] = self._client_id
        validated, key = self.validate_empty(data, ['client_id', 'currency_pair'])
        if not validated:
            raise ValidationError("%s is required" % key)
        response = self.post(self.config.ENDPOINT_URLS['fx_market_rate'], data, authenticated=True, retry=True)
        return response['result']

    def fx_market_rate_with_markup(self, data):
        data['client_id'] = self._client_id
        validated, key = self.validate_empty(data, ['client_id', 'currency_to_buy', 'currency_to_sell',
                                                    'side_of_fx_tx', 'amount'])
        if not validated:
            raise ValidationError("%s is required" % key)

        if data['side_of_fx_tx'] not in ['buy', 'sell']:
            raise ValidationError("Invalid side_of_fx_tx")

        amount_validated, key = self.validate_currency_amount(data, ['amount'])
        if not amount_validated:
            raise ValidationError("%s should be a positive number" % key)

        currency_validated, currency = self.validate_currency(data, ['currency_to_buy', 'currency_to_sell'])
        if not currency_validated:
            raise ValidationError("Invalid %s" % currency)

        # Optional Parameter
        if 'fx_tx_date' in data:
            try:
                datetime.strptime(data['fx_tx_date'], '%Y-%m-%d')
            except ValueError:
                raise ValidationError("Enter valid fx_tx_date in 'YYYY-MM-DD' Format")

        response = self.post(self.config.ENDPOINT_URLS['fx_market_rate_with_mark_up'], data,
                             authenticated=True, retry=True)
        return response['result']

    def change_fx_conversion_delivery_date_quotation(self, data):
        data['client_id'] = self._client_id
        validated, key = self.validate_empty(data, ['path', 'new_date_fx_tx'])
        if not validated:
            raise ValidationError("%s is required" % key)
        try:
            datetime.strptime(data['new_date_fx_tx'], '%Y-%m-%d')
        except ValueError:
            raise ValidationError("Enter valid new_date_fx_tx in 'YYYY-MM-DD' Format")
        response = self.post(self.config.ENDPOINT_URLS['change_fx_conversion_delivery_date_quotation'], data,
                             authenticated=True, retry=True)
        return response['result']

    def change_fx_conversion_value_date(self, data):
        data['client_id'] = self._client_id
        validated, key = self.validate_empty(data, ['path', 'new_date_fx_tx'])
        if not validated:
            raise ValidationError("%s is required" % key)
        try:
            datetime.strptime(data['new_date_fx_tx'], '%Y-%m-%d')
        except ValueError:
            raise ValidationError("Enter valid new_date_fx_tx in 'YYYY-MM-DD' Format")
        response = self.post(self.config.ENDPOINT_URLS['change_fx_conversion_value_date'], data,
                             authenticated=True, retry=True)
        return response['result']

    def retrieve_fx_transaction_record(self, data):
        data['client_id'] = self._client_id
        validated, key = self.validate_empty(data, ['path'])
        if not validated:
            raise ValidationError("%s is required" % key)
        response = self.post(self.config.ENDPOINT_URLS['retrieve_fx_transaction_record'], data,
                             authenticated=True, retry=True)
        return response['result']

    def retrieve_fx_transaction(self, data):
        data['client_id'] = self._client_id
        all_currency_keys = ['currency_to_buy', 'currency_to_sell']
        all_date_keys = ['fx_tx_creation_date_from', 'fx_tx_creation_date_last', 'fx_tx_update_date_from',
                         'fx_tx_update_date_last', 'tx_date_from', 'tx_date_to', 'date_tx_debit_first',
                         'date_tx_debit_last']
        all_amount_keys = ['min_amount_to_buy', 'max_amount_to_buy', 'min_amount_to_sell', 'max_amount_to_sell']
        all_number_keys = ['page_nb', 'result_per_page']
        all_status = ['Funds_to_receive', 'Funds_sent', 'Funds_received', 'FX_deal_settled', 'FX_deal_closed']
        sort_keys = ['amount_to_sell', 'amount_to_buy', 'fx_tx_creation_date', 'fx_tx_update_date', 'currency_to_buy',
                     'currency_to_sell', 'currency_pair', 'date_of_settlement', 'fx_tx_date']
        sort_orders = ['asc', 'desc']
        # All Parameters are optional
        currency_keys = [x for x in all_currency_keys if x in data]
        currency_validated, currency = self.validate_currency(data, currency_keys)
        if not currency_validated:
            raise ValidationError("Invalid %s" % currency)

        amount_keys = [x for x in all_amount_keys if x in data]
        number_keys = [x for x in all_number_keys if x in data]

        amount_validated, key = self.validate_currency_amount(data, amount_keys + number_keys)
        if not amount_validated:
            raise ValidationError("%s should be a positive number" % key)

        date_keys = [x for x in all_date_keys if x in data]
        for key in date_keys:
            try:
                datetime.strptime(data[key], '%Y-%m-%d')
            except ValueError:
                raise ValidationError("Enter valid %s in 'YYYY-MM-DD' Format" % key)

        if 'fx_tx_status' in data and data['fx_tx_status'] not in all_status:
            raise ValidationError("Invalid fx_tx_status")

        if 'sort_order' in data and data['sort_order'] not in sort_keys:
            raise ValidationError('Invalid sort_order')

        if 'sort_asc_to_desc' in data and data['sort_asc_to_desc'] not in sort_orders:
            raise ValidationError('Invalid sort_asc_to_desc')

        response = self.post(self.config.ENDPOINT_URLS['retrieve_fx_transaction'], data,
                             authenticated=True, retry=True)
        return response['result']

    def fx_transaction(self, data):

        data['client_id'] = self._client_id
        all_required = ['side_of_fx_tx','currency_to_buy','currency_to_sell','amount','fx_tx_gtc']
        validated, key = self.validate_empty(data, all_required)
        if not validated:
            raise ValidationError("%s is required" % key)

        all_currency_keys = ['currency_to_buy', 'currency_to_sell']
        currency_keys = [x for x in all_currency_keys if x in data]
        currency_validated, currency = self.validate_currency(data, currency_keys)
        if not currency_validated:
            raise ValidationError("Invalid %s" % currency)

        if data['side_of_fx_tx'] not in ['buy','sell']:
            raise ValidationError("Invalid side_of_fx_tx")

        all_date_keys = ['fx_tx_date']
        date_keys = [x for x in all_date_keys if x in data]
        for key in date_keys:
            try:
                datetime.strptime(data[key], '%Y-%m-%d')
            except ValueError:
                raise ValidationError("Enter valid %s in 'YYYY-MM-DD' Format" % key)

        all_amount_keys = ['amount', 'amount_to_sell', 'amount_to_buy']
        amount_keys = [x for x in all_amount_keys if x in data]
        amount_validated, key = self.validate_currency_amount(data, amount_keys)
        if not amount_validated:
            raise ValidationError("%s should be a positive number" % key)

        if 'fx_tx_gtc' in data and type(data['fx_tx_gtc']) != bool:
            print(type(data['fx_tx_gtc']))
            raise ValidationError("Invalid fx_tx_gtc")
        else:
            data['fx_tx_gtc'] = 'true' if data['fx_tx_gtc'] else 'false'

        response = self.post(self.config.ENDPOINT_URLS['fx_transaction'], data,
                             authenticated=True, retry=True)
        return response['result']
