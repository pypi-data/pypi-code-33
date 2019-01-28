"""
*User: JiltFly
*Date: 2018 / 12 / 4
*Time: 14:25
*email: it.shuaifei@gmail.com
*This is the requests centre
"""
import json
import os
import sys
import time
import requests

from .Config import Config

co = Config
class RequestHttp:
    """
    这是请求数据
    参数 接口url  data
    """
    def post(url,data):
        dataSet = RequestHttp.inForMation(url,data,RequestHttp.getHeader(url))
        return dataSet

    """
    这是请求token
    参数 域名url app_code secret
    """
    def requestToken(url,app_code,secret):
        allocation = {
            "clientId": app_code,
            "secret": secret
        }
        result = requests.post(url + co.apiUrl,json=allocation,headers=co.headers).text
        if result == "unauthorized":
            data = {   "success": False,
                       "message": "iot.auth.InvalidClientKey"
            }
            return data
        result = json.loads(result)
        if result['success'] == False:

            return result
        file = open(co.path,mode="w+")
        jsonArray = {'token':'{'+result["data"]+'}','time':int(time.time())}
        file.write(str(jsonArray))
        file.close()
        return  co.success

    """
    这是请求以后接口的headers
    """
    def requestHead(url,app_code,secret):
        if (os.path.exists(co.path) == False):
            result = RequestHttp.requestToken(url,app_code,secret)
            if result != co.success:
                return result
        file = open(co.path, mode="r")
        jsonToken = file.readline()
        file.close()
        if (len(jsonToken) == 2):
            jsonToken = eval(jsonToken)
            tokenTime = time.time()
            if (co.timeToken < int(tokenTime-jsonToken['time'])):
                result = RequestHttp.requestToken(url,app_code,secret)
                if result != co.success:
                    return result
        else:
            result = RequestHttp.requestToken(url, app_code, secret)
            if result != co.success:
                return result
        return co.success


    def  inForMation(url,data,headers):
        result = requests.post(url,json=data,headers=headers).text
        dataArray = json.loads(result)
        return dataArray

    def getHeader(self):
        file = open(co.path, mode="r")
        jsonToken = file.readline()
        file.close()
        jsonToken = eval(jsonToken)
        headers = {
        "accept": co.accept,
        "connection": co.connection,
        "Content-Type":co.contentType,
        "IrootechAuth" : jsonToken['token'],
        }
        return headers