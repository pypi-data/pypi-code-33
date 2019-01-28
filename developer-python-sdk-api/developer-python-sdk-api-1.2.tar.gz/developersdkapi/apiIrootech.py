"""
*User: JiltFly
*Date: 2018 / 12 / 4
*Time: 14:25
*email: it.shuaifei@gmail.com
"""
import json
import os
import requests
#from numpy.ma.bench import ys

from .src import RequestHttp,Config
re = RequestHttp.RequestHttp
co = Config
class apiIrootech:

    def __init__(self,url,app_code,secret):
        self.__urls = url
        self.app_code = app_code
        self.secret = secret

    def doAction(self,url,data):
        jsonArray = re.post(self.get__url()+url, data)
        if (jsonArray['message'] == co.message):
            return self.token(url,data)
        if (jsonArray['message'] == co.mess):
            return self.token(url,data)
        return jsonArray

    def get__url(self):
        return self.__urls

    def token(self,url,data):
        result = re.requestToken(self.get__url(), self.app_code, self.secret)
        if result != co.success:
            return result
        jsonArray = re.post(self.get__url() + url, data)
        return jsonArray

    def auth(self):
        result = re.requestHead(self.__urls,self.app_code,self.secret)
        if result != co.success:
          try:
              raise RuntimeError(result)
          except RuntimeError as e:
               print(e)
               exit()




