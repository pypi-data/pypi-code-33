import requests

api_endpoint = 'https://portal.mobtexting.com/api/v2/'

class Verify:
    def __init__(self, access_token):
        self.headers = {
            'Accept': 'application/json',
            'Authorization': access_token
        }

    def send(self, to):
        url = api_endpoint + 'verify?to=' + to 
        r = requests.post(url, headers=self.headers)
        return r

    def check(self, id, token):
        url = api_endpoint + 'verify/check/' + id + '/' + token
        r = requests.get(url, headers=self.headers)
        return r
