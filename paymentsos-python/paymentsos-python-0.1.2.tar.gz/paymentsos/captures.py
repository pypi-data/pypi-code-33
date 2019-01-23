class Capture(object):

    def __init__(self, client):
        self.client = client

    def create_capture(self, payment_id, **kwargs):
        headers = self.client._get_private_headers()
        payload = dict()
        payload.update(kwargs)
        endpoint = '/payments/{}/captures'.format(payment_id)
        return self.client._post(self.client.URL_BASE + endpoint, json=payload, headers=headers)

    def retrieve_all_captures(self, payment_id):
        headers = self.client._get_private_headers()
        endpoint = '/payments/{}/captures'.format(payment_id)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers)

    def retrieve_capture(self, *, payment_id, capture_id):
        headers = self.client._get_private_headers()
        endpoint = '/payments/{}/captures/{}'.format(payment_id, capture_id)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers)
