from suds.client import Client
from six import itervalues
from .currencies import GPAY_CURRENCIES

GPAY_PRODUCTION_URL = "https://ecomms2s.sella.it/gestpay/gestpayws/WSs2s.asmx?WSDL"
GPAY_TEST_URL = "https://testecomm.sella.it/gestpay/gestpayws/WSs2s.asmx?WSDL"
GPAY_DEFAULT_CURRENCY = GPAY_CURRENCIES['EUR']['UICCode']

class GestPAY(object):
    def __init__(self, shop_login, test=False):
        self.ws_url = GPAY_TEST_URL if test else GPAY_PRODUCTION_URL
        self.shop_login = shop_login
        try:
            self.client = Client(self.ws_url)
        except Exception as e:
            raise Exception("GestPay WS Endpoint not reachable: {}".format(e))

    def _prepare_request(self):
        data = {}
        data['shopLogin'] = self.shop_login

        return data

    def card_transaction(self, amount, transaction_id, card_number, exp_month, exp_year, currency=GPAY_DEFAULT_CURRENCY, buyer_name=None, buyer_email=None):
        data = self._prepare_request()
        data['amount'] = amount
        data['shopTransactionId'] = transaction_id
        data['cardNumber'] = card_number
        data['expiryMonth'] = exp_month
        data['expiryYear'] = exp_year
        data['uicCode'] = currency

        if buyer_name:
            data['buyerName'] = buyer_name
        if buyer_email:
            data['buyerEmail'] = buyer_email

        return self.make_request('callPagamS2S', data)

    def token_transaction(self, amount, transaction_id, token, currency=GPAY_DEFAULT_CURRENCY, buyer_name=None, buyer_email=None):
        data = self._prepare_request()
        data['amount'] = amount
        data['shopTransactionId'] = transaction_id
        data['tokenValue'] = token
        data['uicCode'] = currency

        if buyer_name:
            data['buyerName'] = buyer_name
        if buyer_email:
            data['buyerEmail'] = buyer_email

        return self.make_request('callPagamS2S', data)

    def read_transaction(self, transaction_id, bank_transaction_id=False):
        data = self._prepare_request()
        data['shopTransactionId'] = transaction_id
        if bank_transaction_id:
            data['bankTransactionId'] = bank_transaction_id

        return self.make_request('CallReadTrxS2S', data)

    def delete_transaction(self, transaction_id, bank_transaction_id=False):
        data = self._prepare_request()
        data['shopTransactionId'] = transaction_id
        if bank_transaction_id:
            data['bankTransactionId'] = bank_transaction_id

        return self.make_request('CallDeleteS2S', data)
            
    def refund_trasnsaction(self, amount, transaction_id, bank_transaction_id, currency=GPAY_DEFAULT_CURRENCY, **kwargs):
        data = self._prepare_request()
        data['amount'] = amount
        data['shopTransactionId'] = transaction_id
        data['bankTransactionId'] = bank_transaction_id
        data['uicCode'] = currency

        for key, value in itervalues(kwargs):
            data[key] = value

        return self.make_request('CallRefundS2S', data)

    def settle_transaction(self, amount, transaction_id, bank_transaction_id=False, currency=GPAY_DEFAULT_CURRENCY):
        data = self._prepare_request()
        data['amount'] = amount
        data['uicCode'] = currency
        data['shopTransID'] = transaction_id
        if bank_transaction_id:
            data['bankTransID'] = bank_transaction_id

        return self.make_request('CallSettleS2S', data)

    def verify_card(self, card_number, exp_month, exp_year, cvv=False, transaction_id=False):
        data = self._prepare_request()
        data['cardNumber'] = card_number
        data['expMonth'] = exp_month
        data['expYear'] = exp_year
        if cvv:
            data['CVV2'] = cvv
        if transaction_id:
            data['shopTransactionId'] = transaction_id

        return self.make_request('callVerifycardS2S', data)
        

    def check_card(self, card_number, exp_month, exp_year, cvv=False, transaction_id=False, card_auth="N"):
        data = self._prepare_request()
        data['cardNumber'] = card_number
        data['expMonth'] = exp_month
        data['expYear'] = exp_year
        if cvv:
            data['CVV2'] = cvv
        if transaction_id:
            data['shopTransactionId'] = transaction_id

        data['withAuth'] = card_auth

        return self.make_request('callCheckCartaS2S', data)

    def update_token(self, card_token, exp_month, exp_year, card_auth="N"):
        data = self._prepare_request()
        data['token'] = card_token
        data['expiryMonth'] = exp_month
        data['expiryYear'] = exp_year
        data['withAut'] = card_auth

        return self.make_request('CallUpdateTokenS2S', data)

    def request_token(self, card_number, exp_month, exp_year, cvv=False, card_auth="N"):
        data = self._prepare_request()
        data['requestToken'] = "MASKEDPAN"
        data['cardNumber'] = card_number
        data['expiryMonth'] = exp_month
        data['expiryYear'] = exp_year

        if cvv:
            data['cvv'] = cvv

        data['withAuth'] = card_auth

        return self.make_request('CallRequestTokenS2S', data)


    def delete_token(self, card_token):
        data = self._prepare_request()
        data['tokenValue'] = card_token

        return self.make_request('callDeleteTokenS2S', data)

    def make_request(self, method, data):
        try:
            response_data = getattr(self.client.service, method)(**data)
            response = response_data['GestPayS2S']
        except Exception as e: 
            response = {"TransactionResult": "KO",
                 "TransactionType": "",
                 "ErrorCode": "-1",
                 "ErrorDescription": "Token service not available ({})".format(e)}

        return response
