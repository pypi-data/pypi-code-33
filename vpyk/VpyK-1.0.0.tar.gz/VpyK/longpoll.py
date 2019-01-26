import requests
import json
import time
        
        
class longpoll:
    def get_longpoll(self):
        self.logging("Getting longpoll server..")
        params = { 
                  'v': self.v, 
                  'access_token': self.token
                 }

        response = requests.get('https://api.vk.com/method/messages.getLongPollServer', params=params)
        lpoll = json.loads(response.text)

        self.key = lpoll['response']['key']
        self.server = lpoll['response']['server']
        self.ts = lpoll['response']['ts']

        self.logging("longpoll server: {}, key: {}, ts: {}".format(self.server, self.key, self.ts))



    def check_longpoll(self):
        params = {
                  'act': 'a_check',
                  'key': self.key, 
                  'ts': self.ts, 
                  'wait': 25
                 }

        response = json.loads(requests.get('https://' + self.server.replace("\\", ""), 
                                           params=params).text)

        if response.get('failed') == 2 or response.get('failed') == 3:
            self.get_longpoll()
            self.check_longpoll()

        if response.get('failed') == 4:
            raise Exception('version is invalid')

        self.ts = response['ts']

        return response


    def logging(self, text):
        if self.log:
            print("--logging" + str(text))


