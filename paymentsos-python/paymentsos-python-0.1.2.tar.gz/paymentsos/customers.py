class Customer(object):

    def __init__(self, client):
        self.client = client

    def create_customer(self, *, customer_reference, first_name=None, last_name=None, email=None,
                        additional_details=None, shipping_address=None):
        headers = self.client._get_private_headers()
        payload = {
            "customer_reference": customer_reference,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "additional_details": additional_details,
            "shipping_address": shipping_address,
        }
        endpoint = '/customers'
        return self.client._post(self.client.URL_BASE + endpoint, json=payload, headers=headers)

    def retrieve_customer_by_reference(self):
        raise NotImplementedError

    def retrieve_customer_by_id(self, customer_id):
        headers = self.client._get_private_headers()
        endpoint = '/customers/{}'.format(customer_id)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers)

    def update_customer(self, *, customer_id, customer_reference, first_name=None, last_name=None, email=None,
                        additional_details=None, shipping_address=None):
        headers = self.client._get_private_headers()
        payload = {
            "customer_reference": customer_reference,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "additional_details": additional_details,
            "shipping_address": shipping_address,
        }
        endpoint = '/customers/{}'.format(customer_id)
        return self.client._put(self.client.URL_BASE + endpoint, json=payload, headers=headers)

    def delete_customer(self, customer_id):
        headers = self.client._get_private_headers()
        endpoint = '/customers/{}'.format(customer_id)
        return self.client._delete(self.client.URL_BASE + endpoint, headers=headers)
