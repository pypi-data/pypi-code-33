name = "paylike"

import requests
from decimal import Decimal


class PaylikeApiClient:
    api_key = None
    merchant_id = None
    api_base_url = "https://api.paylike.io"

    def __init__(self, api_key="", merchant_id=""):
        self.api_key = api_key
        self.merchant_id = merchant_id

    def cancel_transaction(self, transaction_id, amount=None):
        # If Amount was not given cancel the full amount
        if amount is None:
            success, transaction_response = self.get_transaction(transaction_id)
            if not success:
                return False, {};
            amount = transaction_response['pendingAmount']
        else:
            amount = self.convert_to_paylike_amount(amount)

        return self._call_api('/transactions/%s/voids' % transaction_id,
                              method='POST',
                              data={
                                  "amount": amount,
                              })

    def capture_transaction(self, transaction_id, amount, descriptor='', currency=None):
        data = {
            "amount": self.convert_to_paylike_amount(amount),
            "descriptor": descriptor
        }
        if currency is not None:
            data["currency"] = currency

        return self._call_api('/transactions/%s/captures' % transaction_id,
                              method='POST',
                              data=data)

    def create_payment_from_transaction(self, transaction_id, currency, amount, descriptor=''):
        return self._call_api('/merchants/%s/transactions/', method='POST', data={
            "transactionId": transaction_id,
            "descriptor": descriptor,
            "currency": currency,
            "amount": self.convert_to_paylike_amount(amount)
        })

    def create_payment_from_saved_card(self, card_id, currency, amount, descriptor=''):
        return self._call_api('/merchants/%s/transactions/', method='POST', data={
            "cardId": card_id,
            "descriptor": descriptor,
            "currency": currency,
            "amount": self.convert_to_paylike_amount(amount)
        })

    def get_transaction(self, transaction_id):
        result = self._call_api('/transactions/%s' % transaction_id)
        return result[0], result[1]["transaction"]

    def get_transactions(self, limit=100):
        return self._call_api('/merchants/%s/transactions/?limit=%i' % (self.merchant_id, limit))

    def refund_transaction(self, transaction_id, amount, descriptor=""):
        return self._call_api('/transactions/%s/refunds' % transaction_id,
                              method='POST',
                              data={
                                  "amount": self.convert_to_paylike_amount(amount),
                                  "descriptor": descriptor
                              })

    def _call_api(self, uri, method='GET', data={}, headers={}):

        url = "%s%s" % (self.api_base_url, uri)
        auth = ("",self.api_key) if self.api_key is not None else None

        r = requests.request(method, url,
                             json=data if method in ['POST', 'PUT'] else {},
                             headers=headers,
                             params=data if method == 'GET' else {},
                             auth=auth)
        try:
            return (r.status_code in (200, 201), r.json())
        except ValueError:
            return (r.status_code in (200, 201), {})



    def convert_to_paylike_amount(self, amount):
        assert isinstance(amount, Decimal)
        return int(round(amount * 100))