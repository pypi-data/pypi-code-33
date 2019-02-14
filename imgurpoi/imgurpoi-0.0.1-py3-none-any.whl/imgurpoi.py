import os
from pathlib import Path  
 
import requests

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

def imgur_uploader(img_path, id, secret) :
    api_host = 'https://api.imgur.com/3/image'
    headers = { 
    'Authorization' : f'Client-ID {id} Bearer {secret}'
    }
    with open(img_path,'rb') as img :
        files = {'image': img}
        response = requests.post(api_host, files=files, headers=headers)
        #print(response.status_code)
        if response.status_code == 200:
            return { "success" : True, "data": response.json().get("data")}
        else :
            return {"success" : False}
