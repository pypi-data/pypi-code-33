class Token(object):

    def __init__(self, client):
        self.client = client

    def create_token(self, *, holder_name, card_number, credit_card_cvv, expiration_date, token_type='credit_card',
                     identity_document=None, billing_address=None, additional_details=None):
        """
        When creating a Token, remember to use the public-key header instead of the private-key header,
        and do not include the app-id header.

        Args:
            holder_name: Name of the credit card holder.
            card_number: Credit card number.
            credit_card_cvv: The CVV number on the card (3 or 4 digits) to be encrypted.
            expiration_date: Credit card expiration date. Possible formats: mm-yyyy, mm-yy, mm.yyyy,
            mm.yy, mm/yy, mm/yyyy, mm yyyy, or mm yy.
            token_type: The type of token
            billing_address: Address.
            identity_document: National identity document of the card holder.
            additional_details: Optional additional data stored with your token in key/value pairs.

        Returns:

        """
        headers = self.client._get_public_headers()
        payload = {
            "token_type": token_type,
            "credit_card_cvv": credit_card_cvv,
            "card_number": card_number,
            "expiration_date": expiration_date,
            "holder_name": holder_name,
            "identity_document": identity_document,
            "billing_address": billing_address,
            "additional_details": additional_details,
        }
        endpoint = '/tokens'
        return self.client._post(self.client.URL_BASE + endpoint, json=payload, headers=headers)

    def retrieve_token(self, token):
        """
        Retrieve Token details for a specific Token.

        Args:
            token: The identifier of the token.


        Returns:

        """
        headers = self.client._get_private_headers()
        endpoint = '/tokens/{}'.format(token)
        return self.client._get(self.client.URL_BASE + endpoint, headers=headers)
