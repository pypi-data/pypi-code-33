import base64
import requests
import json

class Client:
    """Service"""

    #Variables 
    endpoint = "https://data-gateway-dev.eu-gb.mybluemix.net/data"
    client_secret = ""
    device_token = ""

    #Initialize
    def __init__(self,client_secret,device_token):

        #set variables
        self.client_secret = client_secret
        self.device_token = device_token

        return
    
    def generate_auth_token(self,client_secret,device_token):

        token = ""
        
        if not(
            client_secret.strip() and
            device_token.strip()
        ):
            token = ""
        else:
            token = base64.b64encode(client_secret + ":" + device_token)
        
        return token

    def send_data(self,device_entities):

        if not self.generate_auth_token(self.client_secret,self.device_token).strip():
           return "Client Secret and Device Token can not be empty"

        else:
            try:
                print(self.generate_auth_token(self.client_secret,self.device_token))
                response = requests.post(self.endpoint,
                    headers={
                        "Authorization":"Basic " + self.generate_auth_token(self.client_secret,self.device_token),
                        "Content-Type":"application/json"
                    },
                    data=json.dumps(device_entities)
                )
                print(response.status_code)
                print("Response: {content}".format(content = response.content))
            except requests.exceptions.RequestException:
                print("Sending data failed, check network connection")

        return "OK"




  