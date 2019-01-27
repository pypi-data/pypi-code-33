import json
#import pandas as pd

class Response:
    
    def __init__(self, response, headers, print_warnings = True):
        self.__warnings = None
        self.__errors = None
        self.__shards = None
        self.__configuration = None
        try:
            if "x-broker-errors" in headers:
                self.__errors = int(headers["x-broker-errors"])
                if print_warnings & self.__errors > 0:
                    print("Error(s) for this request")
            if "x-broker-warnings" in headers:
                self.__warnings = int(headers["x-broker-warnings"])
                if print_warnings & self.__warnings > 0:
                    print("Warning(s) for this request")  
            if "x-broker-shards" in headers:
                self.__shards = int(headers["x-broker-shards"]) 
            if "x-broker-configuration" in headers:
                self.__configuration = str(headers["x-broker-configuration"])            
        except:
            pass                 
        if type(response) == str:
            try:
                self.__response = json.loads(response)
            except json.JSONDecodeError as decodeErr:
                print ("JSON Decode Error:",decodeErr) 
                raise Exception("no (valid) response from broker")
        else:
            raise Exception("response must be of type str")
            
    def __repr__(self):
        description = "Broker Response"
        if self.__warnings:
            description += "\n- {0} warnings(s) for this request".format(self.__warnings)
        if self.__errors:
            description += "\n- {0} error(s) for this request".format(self.__errors)
        try:
            ntot = self.__response["response"]["numFound"]            
        except:
            ntot = 0
            pass
        try:
            ndocs = len(self.__response["response"]["docs"])            
        except:
            ndocs = 0
            pass
        description += "\n- documents: {0} from {1}".format(ndocs, ntot)
        if ndocs>0:
            try:
                start = self.__response["response"]["start"]            
            except:
                start = 0
            description += ", starting at {0}".format(start)
        if "facet_counts" in self.__response:    
            description += "\n- facet_counts:"
            if ("facet_queries" in self.__response["facet_counts"]) & bool(self.__response["facet_counts"]["facet_queries"]): 
                description += "\n  - facet_queries ({0})".format(len(self.__response["facet_counts"]["facet_queries"]))
            if ("facet_fields" in self.__response["facet_counts"]) & bool(self.__response["facet_counts"]["facet_fields"]): 
                description += "\n  - facet_fields ({0})".format(len(self.__response["facet_counts"]["facet_fields"]))
            if ("facet_ranges" in self.__response["facet_counts"]) & bool(self.__response["facet_counts"]["facet_ranges"]): 
                description += "\n  - facet_ranges ({0})".format(len(self.__response["facet_counts"]["facet_ranges"]))
            if ("facet_intervals" in self.__response["facet_counts"]) & bool(self.__response["facet_counts"]["facet_intervals"]): 
                description += "\n  - facet_intervals ({0})".format(len(self.__response["facet_counts"]["facet_intervals"]))
            if ("facet_heatmaps" in self.__response["facet_counts"]) & bool(self.__response["facet_counts"]["facet_heatmaps"]): 
                description += "\n  - facet_heatmaps ({0})".format(len(self.__response["facet_counts"]["facet_heatmaps"]))
        return(description)    
    
    def raw(self): 
        return(self.__response)
    
    def configuration(self):
        return(self.__configuration)
    
    def shards(self):
        return(self.__shards)
    
    def warnings(self):
        return(self.__warnings)
    
    def errors(self):
        return(self.__errors)
    
    def numFound(self): 
        try:
            return(self.__response["response"]["numFound"])
        except:
            return(None)
        
    def start(self): 
        try:
            return(self.__response["response"]["start"])
        except:
            return(None)    
    
    def docs(self): 
        try:
            return(self.__response["response"]["docs"])
            #return(pd.DataFrame(self.__response["response"]["docs"]))
        except:
            return(None)
        
        
        
