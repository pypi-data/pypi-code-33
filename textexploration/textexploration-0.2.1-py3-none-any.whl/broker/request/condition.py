
class Condition:
    
    def __init__(self):
        self.__type = None
        self.__allowNot = None
        self.__allowFacetquery = None
        self.__allowExpansion = None
        self.__condition = {
        }  
        
    def type(self):
        return(self.__type) 
    
    def raw(self): 
        """Get the condition object"""
        if self.__type is None:
            raise Exception("no (valid) condition")
        self.__condition["type"] = self.__type
        return(self.__condition)
    
    def param_not(self, value):
        """Negation of the condition"""
        if self.__allowNot:
            try:
                currentNot = self.__condition["not"]
            except Exception:
                currentNot = None
            if type(value) is bool:
                self.__condition["not"] = value
            elif not (value is None):
                raise Exception("value must be a boolean")
            return(currentNot)
        else:
            raise Exception("negation not implemented for this condition")
        
    def param_expansion(self, expansion):
        """Applied expansion for the condition"""
        if self.__allowExpansion:
            try:
                currentExpansion = self.__condition["expansion"]
            except Exception:
                currentExpansion = None
            if type(expansion) is Expansion:
                self.__condition["expansion"] = expansion.raw()
            elif not (expansion is None):
                raise Exception("value must be an expansion")
            return(currentExpansion)
        else:
            raise Exception("expansion not implemented for this condition")    
        
    def param_facetquery(self, value):
        """Create facetquery from condition"""
        if self.__allowFacetquery:
            #get current
            try:
                currentFacetquery = self.__condition["facetquery"]
            except Exception:
                currentFacetquery = None
            try:
                currentKey = self.__condition["key"]
            except Exception:
                currentKey = None   
            #update
            if type(value) is bool:
                self.__condition["facetquery"] = value
                #remove previous key    
                try:
                    del self.__condition["key"]
                except:
                    pass
            elif type(value) is str:
                self.__condition["facetquery"] = True
                self.__condition["key"] = value
            elif not(value is None):
                raise Exception("value must be a boolean or string")
            if not (currentKey is None):
                return currentKey
            else:
                return currentFacetquery
        else:
            raise Exception("negation not implemented for this condition")       
        
class ConditionEquals(Condition):
    
    def __init__(self, field, value):
        super().__init__()
        self.__type = "equals"
        self.__allowNot = True
        self.__allowFacetquery = True
        self.__allowExpansion = True
        if not(type(field) is str):
            raise Exception("field must be a string")
        self.__condition["field"] = field
        if not ((type(value) is str) | (type(value) is bool) | (type(value) is list)):
            raise Exception("value must be a string, boolean or list of strings or booleans")
        self.__condition["value"] = value
        
class ConditionPhrase(Condition):
    
    def __init__(self, field, value):
        super().__init__()
        self.__type = "phrase"
        self.__allowNot = True
        self.__allowFacetquery = True
        self.__allowExpansion = True
        if not(type(field) is str):
            raise Exception("field must be a string")
        self.__condition["field"] = field
        if not ((type(value) is str) | (type(value) is list)):
            raise Exception("value must be a string or list of strings")
        self.__condition["value"] = value        
 
class ConditionWildcard(Condition):
    
    def __init__(self, field, value):
        super().__init__()
        self.__type = "wildcard"
        self.__allowNot = True
        self.__allowFacetquery = True
        if not(type(field) is str):
            raise Exception("field must be a string")
        self.__condition["field"] = field
        if not ((type(value) is str) | (type(value) is list)):
            raise Exception("value must be a string or list of strings")
        self.__condition["value"] = value        

class ConditionRegexp(Condition):
    
    def __init__(self, field, value):
        super().__init__()
        self.__type = "regexp"
        self.__allowNot = True
        self.__allowFacetquery = True
        if not(type(field) is str):
            raise Exception("field must be a string")
        self.__condition["field"] = field
        if not ((type(value) is str) | (type(value) is list)):
            raise Exception("value must be a string or list of strings")
        self.__condition["value"] = value        

class ConditionRange(Condition):
    
    def __init__(self, field, start, end):
        super().__init__()
        self.__type = "range"
        self.__allowNot = True
        self.__allowFacetquery = True
        if not(type(field) is str):
            raise Exception("field must be a string")
        self.__condition["field"] = field        
        if not(start is None):
            if not ((type(start) is str) ):
                raise Exception("start must be a string")
            else:
                self.__condition["start"] = start   
        if not(end is None):
            if not ((type(end) is str) ):
                raise Exception("end must be a string")
            else:
                self.__condition["end"] = end            


class ConditionCQL(Condition):
    
    def __init__(self, field, value):
        super().__init__()
        self.__type = "cql"
        self.__allowNot = True
        self.__allowFacetquery = True
        if not(type(field) is str):
            raise Exception("field must be a string")
        self.__condition["field"] = field
        if not ((type(value) is str) | (type(value) is list)):
            raise Exception("value must be a string or list of strings")
        self.__condition["value"] = value      
        
class Expansion:
    
    def __init__(self, value, parameters):
        if not(type(value) is str):
            raise Exception("value must be a string")
        self.__expansion = {
            "type" : value
        }  
        if type(parameters) is dict:
            self.__expansion["parameters"] = parameters       
        elif not(parameters is None):
            raise Exception("parameters must be a dict")
        
    def raw(self): 
        """Get the expansion object"""
        return(self.__expansion)        
            