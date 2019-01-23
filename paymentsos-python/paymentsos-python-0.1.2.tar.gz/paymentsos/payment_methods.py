class PaymentMethod(object):

    def __init__(self, client):
        self.client = client

    def create_payment_method(self, *, customer_id, token):
        headers = self.client._get_private_headers()
        endpoint = '/customers/{}/payment-methods/{}'.format(customer_id, token)
        return self.client._post(self.client.URL_BASE + endpoint, headers=headers)

    def retrieve_all_payment_methods(self, *, customer_id, query_params=None):
        headers = self.client._get_private_headers()
        endpoint = '/customers/{}/payment-methods'.format(customer_id)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers, params=query_params)

    def retrieve_payment_method(self, *, customer_id, token):
        headers = self.client._get_private_headers()
        endpoint = '/customers/{}/payment-methods/{}'.format(customer_id, token)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers)

    def delete_payment_method(self, *, customer_id, token):
        headers = self.client._get_private_headers()
        endpoint = '/customers/{}/payment-methods/{}'.format(customer_id, token)
        return self.client._delete(self.client.URL_BASE + endpoint, headers=headers)
