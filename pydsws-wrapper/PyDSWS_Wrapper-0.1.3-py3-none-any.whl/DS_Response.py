# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 19:51:02 2019

@author: Vidya Dinesh
"""
import requests
import json
import pandas as pd
import datetime

import DS_Requests as DSReq

class DataStream:
    url = "http://product.datastream.com/DSWSClient/V1/DSService.svc/rest/"
    username = ""
    password = ""
    token = None
    dataSource = None
    
    def __init__(self, username, password, dataSource=None):
        DataStream.username = username
        DataStream.password = password
        DataStream.dataSource = dataSource
    
    @staticmethod
    def Get_Token():
        token_url = DataStream.url + "GetToken"
        tokenReq = DSReq.TokenRequest(DataStream.username, DataStream.password, DataStream.dataSource)
        raw_tokenReq = tokenReq.Get_Raw_TokenRequest()
        json_tokenReq = DataStream._JSON_Request(raw_tokenReq)
        #Post the token request to get response in json format
        json_Response = requests.post(token_url, json=json_tokenReq).json()
        DataStream.token = json_Response["TokenValue"]
        
    @staticmethod
    def _JSON_Request(raw_text):
        #convert the dictionary (raw text) to json text first
        jsonText = json.dumps(raw_text)
        byteTemp = bytes(jsonText,'utf-8')
        byteTemp = jsonText.encode('utf-8')
        #convert the json Text to json formatted Request
        jsonRequest = json.loads(byteTemp)
        return jsonRequest
        
    def Get_Data(self, req):
        getData_url = DataStream.url + "GetData"
        raw_dataRequest = ""
        json_dataRequest = ""
        json_Response = ""
        
        datarequest = DSReq.DataRequest()
        if (DataStream.token == None):
            return "Invalid Token Value"
        else:
            datarequest.Set_Data(req, DataStream.dataSource, DataStream.token)
            raw_dataRequest = datarequest.Get_Raw_Datarequest()
        
        if (raw_dataRequest != ""):
            json_dataRequest = DataStream._JSON_Request(raw_dataRequest)
            #Post the requests to get response in json format
            json_Response = requests.post(getData_url, json=json_dataRequest).json()
            #print(json_Response)
            #format the JSON response into readable table
            response_dataframe = self._format_Response(json_Response['DataResponse'])
            
        return response_dataframe
    
    def Get_Bundle_data(self, bundleRequest=[]):
        getDataBundle_url = DataStream.url + "GetDataBundle"
        raw_dataRequest = ""
        json_dataRequest = ""
        json_Response = ""
        
        datarequest = DSReq.DataRequest()
        if (DataStream.token == None):
            return "Invalid Token Value"
        else:
            datarequest.Set_Bundle_Data(bundleRequest, DataStream.dataSource, DataStream.token)
            raw_dataRequest = datarequest.Get_Raw_Bundle_Datarequest()
            #print(raw_dataRequest)
            
        if (raw_dataRequest != ""):
            json_dataRequest = DataStream._JSON_Request(raw_dataRequest)
            #Post the requests to get response in json format
            json_Response = requests.post(getDataBundle_url, json=json_dataRequest).json()
            #print(json_Response)
            response_dataframe = self._format_bundle_response(json_Response)
            
        return response_dataframe
    
    @staticmethod
    def _get_Date(jsonDate):
        d = jsonDate[6:-10]
        d = float(d)
        d = datetime.datetime.utcfromtimestamp(d).strftime('%Y-%m-%d')
        return d
    
    @staticmethod
    def _get_DatatypeValues(jsonDTValues):
        df = pd.DataFrame()
        multiIndex = False
        valDict = {"Instrument":[],"Datatype":[],"Value":[]}
       
        for item in jsonDTValues: 
           datatype = item['DataType']
           for i in item['SymbolValues']:
               instrument = i['Symbol']
               valDict["Datatype"].append(datatype)
               valDict["Instrument"].append(instrument)
               values = i['Value']
               valType = i['Type']
               colNames = (instrument,datatype)
               df[colNames] = None
            
               #Handling all possible types of data as per DSSymbolResponseValueType
               if valType in [7, 8, 10, 11, 12, 13, 14, 15, 16]:
                   df[colNames] = values
                   multiIndex = True
               elif valType in [1, 2, 3, 5, 6]:
                   #df[colNames]= values
                   valDict["Value"].append(values)
                   multiIndex = False
               else:
                   if valType == 4:
                       values = DataStream._get_Date(values)
                       #df[colNames]= values
                       valDict["Value"].append(values)
                       multiIndex = False
                   elif valType == 9:
                       multiIndex = True
                       date_array = []
                       for eachVal in values:
                           date_array.append(DataStream._get_Date(eachVal))
                           df[colNames] = values
                   else:
                       if valType == 0:
                           multiIndex = False
                           #df[colNames]= values = 'Error'
                           valDict["Value"].append(values)
        if multiIndex:  
            df.columns = pd.MultiIndex.from_tuples(df.columns, names=['Instrument', 'Field'])
            return df
        else:
            indexLen = range(len(valDict['Instrument']))
            newdf = pd.DataFrame(data=valDict,columns=["Instrument", "Datatype", "Value"],
                                 index=indexLen)
            return newdf
            
       
        
        
    @staticmethod
    def _format_Response(response_json):
        # If dates is not available, the request is not constructed correctly
        response_json = dict(response_json)
        if 'Dates' in response_json.keys():
            dates_converted = []
            if response_json['Dates'] != None:
                dates = response_json['Dates']
                for d in dates:
                    dates_converted.append(DataStream._get_Date(d))
        else:
            return 'Error - please check instruments and parameters (time series or static)'
        
        # Loop through the values in the response
        dataframe = DataStream._get_DatatypeValues(response_json['DataTypeValues'])
        if (len(dates_converted) == len(dataframe.index)):
            if (len(dates_converted) > 1):
                dataframe.insert(loc = 0, column = 'Dates', value = dates_converted)
        elif (len(dates_converted) == 1):
            dataframe['Dates'] = dates_converted[0]
            
        return dataframe

    
    @staticmethod
    def _format_bundle_response(response_json):
       formattedResp =[]
       for eachDataResponse in response_json['DataResponses']:
           df = DataStream._format_Response(eachDataResponse)
           formattedResp.append(df)      
           
       return formattedResp

    def Post_user_request(self, inst, dtypes=[], start = "",freq ="D", end = ""):
        index = inst.rfind('|')
        if index == -1:
            instrument = DSReq.Instrument(inst, None)
        else:
            props = []
            if inst[index+1:].rfind(',') != -1:
                propList = inst[index+1:].split(',')
                for eachProp in propList:
                    props.append(DSReq.IProperties(eachProp, True))
            else:
                props.append(DSReq.IProperties(inst[index+1:], True))
            instrument = DSReq.Instrument(inst[0:index], props)
        datypes = []
        if len(dtypes) > 0:
            for eachDtype in dtypes:
                datypes.append(DSReq.DataType(eachDtype))
        date = DSReq.Date(start, freq, end)
        
        request = {"Instrument":instrument,"Datatypes":datypes,"Date":date}
        
        return request
  

#ds = DataStream("ZDSM042", "alpha893", "PROD")
#ds.Get_Token()
#reqs = ds.Post_user_request("VOD")
#df = ds.Get_Data(reqs)
#print(df)              
