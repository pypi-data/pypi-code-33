import requests

class Client:
    def __init__(self, access_token):
        self.access_token = access_token

    def send(self, to, _from, body, service='T'):
        api_endpoint = 'https://portal.mobtexting.com/api/v2/'
        url = api_endpoint + 'sms/send?access_token=' + self.access_token + '&message=' \
                    + body  + '&sender='+ _from + '&to=' + to + '&service=' + service
        r = requests.get(url)
        return r
