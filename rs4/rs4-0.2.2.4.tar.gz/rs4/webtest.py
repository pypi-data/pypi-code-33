# pytest framework ---------------------------------------------
import requests
from rs4 import siesta
import time
import sys
import os
import xmlrpc.client 

class Target:
    def __init__ (self, endpoint):
        self.__endpoint = endpoint
        self.__api = siesta.API (endpoint, reraise_http_error = False)
        self.__requests = Requests (endpoint)
    
    def __enter__ (self):
        return self
        
    def __exit__ (self, type, value, tb):
        self._close ()
    
    def __getattr__ (self, attr):
        if attr in ("get", "post", "put", "patch", "delete", "head", "options", "xmlrpc", "rpc", "jsonrpc", "grpc"):
            return getattr (self.__requests, attr)
        return getattr (self.__api, attr)
        
    def __del__ (self):
        self._close ()
            
    def _close (self):
        pass


class Requests:
    def __init__ (self, endpoint):
        self.endpoint = endpoint
        self.s = requests.Session ()        
    
    def resolve (self, url):
        if url.startswith ("http://") or url.startswith ("https://"):
            return url
        else:
            return self.endpoint + url 
        
    def get (self, url, *args, **karg):
        return self.s.get (self.resolve (url), *args, **karg)
        
    def post (self, url, *args, **karg):
        return self.s.post (self.resolve (url), *args, **karg)
    
    def put (self, url, *args, **karg):
        return self.s.put (self.resolve (url), *args, **karg)
    
    def patch (self, url, *args, **karg):
        return self.s.patch (self.resolve (url), *args, **karg)
    
    def delete (self, url, *args, **karg):
        return self.s.delete (self.resolve (url), *args, **karg)
    
    def head (self, url, *args, **karg):
        return self.s.head (self.resolve (url), *args, **karg)
                
    def options (self, url, *args, **karg):
        return self.s.options (self.resolve (url), *args, **karg)
    
    def rpc (self, url):
        return xmlrpc.client.ServerProxy (self.resolve (url))
    xmlrpc = rpc
    
    def jsonrpc (self, url):
        import jsonrpclib
        return jsonrpclib.ServerProxy (self.resolve (url))
    