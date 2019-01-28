import json

import requests

from .config import SDKConfig


"""
这是http  
获取token
"""
class result:
      def post(url,data):
          result = requests.post(url + SDKConfig.LOGIN_URL,json=data,headers=SDKConfig.header).text
          dataArray = json.loads(result)
          try:
              if dataArray["success"] == SDKConfig.SUCCESS:
                 return dataArray["data"]
              else:
                  raise RuntimeError("Token fetch failed ")
          except:
              raise RuntimeError("Token fetch failed ")
