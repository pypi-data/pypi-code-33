class Charge(object):

    def __init__(self, client):
        self.client = client

    def create_charge(self, *, payment_id, payment_method, reconciliation_id=None, provider_specific_data=None,
                      user_agent=None, ip_address=None, **kwargs):
        headers = self.client._get_private_headers()
        headers.update({
            'x-client-user-agent': user_agent,
            'x-client-ip-address': ip_address,
        })
        payload = {
            "payment_method": payment_method,
            "provider_specific_data": provider_specific_data,
            "reconciliation_id": reconciliation_id
        }
        payload.update(kwargs)
        endpoint = '/payments/{}/charges'.format(payment_id)
        return self.client._post(self.client.URL_BASE + endpoint, json=payload, headers=headers)

    def retrieve_all_charges(self, *, payment_id, query_params=None):
        headers = self.client._get_private_headers()
        endpoint = '/payments/{}/charges'.format(payment_id)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers, params=query_params)

    def retrieve_charge(self, *, payment_id, charge_id, query_params=None):
        headers = self.client._get_private_headers()
        endpoint = '/payments/{}/charges/{}'.format(payment_id, charge_id)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers, params=query_params)
