import requests

CHECKIT_URL = 'https://checkit-api.donodoo.it/v2'

class Checkit(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.creditcards = CreditCardResource('pro/creditcard/', api_key)


class CheckitResource(object):
    def __init__(self, endpoint, api_key):
        self.endpoint = endpoint
        self.api_key = api_key
    
    @property
    def url(self):
        return "{}/{}".format(CHECKIT_URL, self.endpoint)
    
    @property
    def headers(self):
        return {
            'Authorization': 'Token ' + self.api_key
        }
    
    def check(self, data):
        response = requests.post(self.url, data=data, headers=self.headers)
        response.raise_for_status()

        return response.json()

class CreditCardResource(CheckitResource):
    def check(self, number):
        return super(CreditCardResource, self).check({
            "number": number
        })
    
