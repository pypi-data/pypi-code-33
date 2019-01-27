import requests
import json
from .request.request import Request
from .response.response import Response

class Broker:
    
    def __init__(self, url):
        #define url
        self.__url = url
        self.__timeout = 180
        self.__key = None
        
    def set_key(self, value): 
        if ((value is None) | (type(value) is str)):
            self.__key = value
        else :
            raise Exception("value must be a string")
                 
        
    def do_request(self, request, show_messages=True):    
        """Perform a BrokerRequest"""
        if type(request) == Request:
            data = json.dumps(request.raw())  
        elif type(request) == dict:
            data = json.dumps(request)  
        elif type(request) == str:
            data = request
        else:
            raise Exception("unsupported type of request")  
        try: 
            headers = {"Accept": "application/json"}
            if self.__key!=None:
                headers.update({"X-Broker-key": self.__key})            
            response = requests.post(self.__url, data, timeout=self.__timeout, headers=headers)
            response.raise_for_status() 
            return(Response(response.text, response.headers, show_messages))                        
        except requests.exceptions.HTTPError as httpErr: 
            if show_messages:
                print ("Http Error:",httpErr) 
            try:
                return(Response(response.text, response.headers, False))   
            except:
                return None          
        except requests.exceptions.ConnectionError as connErr: 
            if show_messages:
                print ("Error Connecting:",connErr) 
            return(None)
        except requests.exceptions.Timeout as timeOutErr: 
            if show_messages:
                print ("Timeout Error:",timeOutErr) 
            return(None)
        except requests.exceptions.RequestException as reqErr: 
            if show_messages:
                print ("Something Else:",reqErr) 
            return(None)
        raise Exception("no (valid) response from broker")
        
        
