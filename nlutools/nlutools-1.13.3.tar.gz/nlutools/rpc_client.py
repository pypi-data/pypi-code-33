import requests
import json

from utils import *
from config import supportConf

http_headers = {"Content-type":"application/json"}

def doTask(taskUrl,serverName,data):
    try:
        data = json.dumps({'server_name':serverName,'traffic_paramsDict':data})
        #print(data)
        ret = requests.post(taskUrl,data,headers=http_headers)
        response_status = ret.status_code
        if response_status == 200:
            result = json.loads(ret.text)
            if result['status']==True:
                return result['result']
            return None
        else:
            printException('response error with status code:%s '%response_status)
            printException('please contact supporter %s for this exception'%(supportConf[serverName]))
            return None
    except Exception as e:
        printException('%s exception \nplease contact supporter %s for this exception : \n%s'%(serverName,supportConf[serverName],e))
