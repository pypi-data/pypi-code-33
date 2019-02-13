# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 00:55:39 2018

@author: Vidya Dinesh
"""
# Properties of Datatypes and Instruments
class IProperties:
    Key = ""
    Value = True
    
    def __init__(self, key, value):
        self.Key = key
        self.Value = value
        
class DataType(IProperties):
    datatype = ""
    
    def __init__(self, value, propKey=None, propVal=None):
        self.Key = propKey
        self.Value = propVal
        self.datatype = value
        
class Date:
    Start = ""
    End = ""
    Frequency = ""
    Kind = 0
    
    def __init__(self, startDate = "", freq = "D", endDate = ""):
       self.Start = startDate
       self.End = endDate
       self.Frequency = freq
       if (startDate != ""):
           self.Kind = 1
       else:
           self.Kind = 0
       
                
#Each instrument has array of properties
class Instrument(IProperties):
    instrument = ""
    properties = [IProperties]
    
    def __init__(self, inst, props=None):
        self.instrument = inst
        self.properties = props
    

class Properties:
    Key = "Source"
    Value = ""
    
    def __init__(self, value):
        self.Value = value
        
class TokenValue:
    Token = ""
    
    @staticmethod
    def Set_Token(token):
        TokenValue.Token = token
        
class TokenRequest(Properties):
    password = ""
    username = ""
    
    def __init__(self, uname, pword, source = None):
        self.username = uname
        self.password = pword
        self.Key = "Source"
        self.Value = source
        
    def Get_Raw_TokenRequest(self):
        tokenReq = {"Password":self.password,"Properties":[],"UserName":self.username}
        if self.Value == None or self.Value == "":
            tokenReq["Properties"] = None
        else:
            tokenReq["Properties"].append({"Key":self.Key,"Value":self.Value})
        
        return tokenReq
    
class DataRequest:
    
    def Set_Bundle_Data(self, requests=[], source=None, token=""):
        for eachReq in requests:
            self._Set_Datatypes(eachReq["Datatypes"])
            self._Set_Date(eachReq["Date"])
            self._Set_Instrument(eachReq["Instrument"])
            self.datarequests["DataRequests"].append({"DataTypes":self.datatypes["DataTypes"],
                             "Instrument":self.instrument["Instrument"], "Date":self.date["Date"], "Tag":self.tag["Tag"]
                             })
        self._Set_SourceProperties(source)
        self._Set_Token(token)
        
    def Set_Data(self, request_dict, source=None, token=""):
        self._Set_Datatypes(request_dict["Datatypes"])
        self._Set_Date(request_dict["Date"])
        self._Set_Instrument(request_dict["Instrument"])
        self._Set_SourceProperties(source)
        self._Set_Token(token)
    
    # Variables needed for building datarequest
    hints = {"E":"IsExpression", "L":"IsList", "RC":"ReturnCurrency"}
    datatypes = {"DataTypes":[]}
    instrument = {"Instrument":{}}
    date = {"Date":{}}
    tag = {"Tag":None}
    
    datarequest = {"DataRequest":{},"Properties":None,"TokenValue":""}
    datarequests = {"DataRequests":[],"Properties":None,"TokenValue":""}
    properties = {"Properties":None}
    tokenValue = {"TokenValue":""}
    
    def _Set_Datatypes(self, dtypes=None):
        self.datatypes["DataTypes"]=[]
        for eachDtype in dtypes:
            if eachDtype.datatype == None:
                continue
            if eachDtype.Key == None:
                self.datatypes["DataTypes"].append({"Properties":None, "Value":eachDtype.datatype})
            else:
                if eachDtype.Key == "RN":
                    self.datatypes["DataTypes"].append({"Properties":{"Key":DataRequest.hints[eachDtype.Key],"Value":True},
                          "Value":eachDtype.datatype})
        
    def _Set_Instrument(self, inst):
        propties = []
        if inst.properties == None:
            self.instrument["Instrument"] = {"Properties":None,"Value":inst.instrument}
        else:
            for eachPrpty in inst.properties:
                propties.append({"Key":DataRequest.hints[eachPrpty.Key],"Value":True})
            self.instrument["Instrument"] = {"Properties":propties,"Value":inst.instrument}
            
    
    def _Set_Date(self, dt):
        self.date["Date"] = {"End":dt.End,"Frequency":dt.Frequency,"Kind":dt.Kind,"Start":dt.Start}
        
    
    def _Set_SourceProperties(self, source):
        if source != None:
            self.properties["Properties"]=({"Key":"Source","Value":source})
    
    def _Set_Token(self, token):
        if token != "":
            self.tokenValue["TokenValue"] = token
        
    
    def Get_Raw_Bundle_Datarequest(self):
       
        self.datarequests["Properties"] = self.properties["Properties"]
        self.datarequests["TokenValue"] = self.tokenValue["TokenValue"]
        return self.datarequests
    
    def Get_Raw_Datarequest(self):
        self.datarequest["DataRequest"] = {"DataTypes":self.datatypes["DataTypes"],
                        "Date":self.date["Date"],
                        "Instrument":self.instrument["Instrument"],
                        "Tag":self.tag["Tag"]}
        self.datarequest["Properties"] = self.properties["Properties"]
        self.datarequest["TokenValue"] = self.tokenValue["TokenValue"]
        return self.datarequest
         
        

            
    
#Datatypes
#dat =[]
#dat.append(DataType("PH"))
#dat.append(DataType("PL","RN"))
#dat.append(DataType("P","RN",True))
#Instrument
#Props = [IandDT_Properties("RN", True), IandDT_Properties("E", True)]
#ins = Instrument("VOD", Props)
#Date
#dt = Date()
#dt = dt.Set_Date("20180101","M")
#
#dr = DataRequest()
#dr.Set_Datatypes(dat)
#dr.Set_Instrument(ins)
#dr.Set_Date(dt)
#
#datareq = dr.Get_Raw_Datarequest()
#print(datareq)




#    
    


    
    
        
        
    

