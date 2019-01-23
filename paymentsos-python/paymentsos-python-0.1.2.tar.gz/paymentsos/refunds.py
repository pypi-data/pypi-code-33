class Refund(object):

    def __init__(self, client):
        self.client = client

    def create_refund(self, payment_id):
        headers = self.client._get_private_headers()
        endpoint = '/payments/{}/refunds'.format(payment_id)
        return self.client._post(self.client.URL_BASE + endpoint, headers=headers)

    def retrieve_all_refunds(self, payment_id):
        headers = self.client._get_private_headers()
        endpoint = '/payments/{}/refunds'.format(payment_id)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers)

    def retrieve_refund(self, *, payment_id, refund_id):
        headers = self.client._get_private_headers()
        endpoint = '/payments/{}/refunds/{}'.format(payment_id, refund_id)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers)
