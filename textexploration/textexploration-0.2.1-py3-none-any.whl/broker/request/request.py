import json
from .condition import Condition
from .documents import Documents

class Request:
    
    def __init__(self):
        self.__request = {
            "response" : {
                "documents": {}
            }
        }
        
    def __repr__(self):
        return(json.dumps(self.__request))
        
    def raw(self): 
        """Get the request object"""
        return(self.__request)
    
    def cache(self, cache = None): 
        """Get and optionally change current setting cache"""
        try:
            currentCache = self.__request["cache"]
        except Exception:
            currentCache = None
        if type(cache) is bool:
            self.__request["cache"] = cache
        elif not (cache is None):
            raise Exception("cache must be of type bool") 
        return(currentCache)
    
    def condition(self, condition = None):
        """Get and optionally change current condition"""
        try:
            currentCondition = self.__request["condition"]
        except Exception:
            currentCondition = None
        if isinstance(condition, Condition):
            self.__request["condition"] = condition.raw()
        elif not (condition is None):
            raise Exception("invalid condition") 
        return(currentCondition)
    
    def documents(self, documents = None):
        """Get and optionally change current documents"""
        try:
            currentDocuments = self.__request["response"]["documents"]
        except Exception:
            currentDocuments = None
        if isinstance(documents, Documents):
            self.__request["response"]["documents"] = documents.raw()
        elif not (documents is None):
            raise Exception("invalid condition") 
        return(currentDocuments)
