__author__ = 'zhuxietong'
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from .response import ApiState
from .crossdomain import crossdomain
import json


from django.conf import settings

ApiCode = 'status'
ApiData = 'data'
ApiMessage = 'message'

try:
    if settings.ApiCode is not None:
        ApiCode = settings.ApiCode
except Exception as e:
    pass
try:
    if settings.ApiData is not None:
        ApiData = settings.ApiData
except Exception as e:
    pass

try:
    if settings.ApiMessage is not None:
        ApiMessage = settings.ApiMessage
except Exception as e:
    pass



class EeException(APIException):
    def __init__(self, instance,line=None,file=None):
        super(EeException,self).__init__(instance)


def paw_message(data):
    if isinstance(data, str):
        detail = data
    elif isinstance(data, dict):
        infos = []
        print(data)
        for key, value in data.items():
            msg = paw_message(value)
            one_message = "%s:%s" % (key,msg)
            print(one_message)
            infos.append(one_message)
        detail = ';'.join(infos)
    elif isinstance(data,list):
        infos = []
        for value in data:
            one_msg = paw_message(value)
            infos.append(one_msg)
        detail = ';'.join(infos)
    else:
        detail = json.dumps(data)
    return  detail


@crossdomain('')
def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    # print("===DD",type(exc))
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None:
        message = paw_message(response.data)
        data = {
            ApiCode:ApiState.exception.value,
            ApiData:{},
            ApiMessage:message
        }
        response.data = data
        response.status_code = 200

    else:
        data = {}
        data[ApiCode] = ApiState.exception.value
        data[ApiData] = None
        data[ApiMessage] = str(exc)
        response = Response(data=data, status=200, headers=None)
        response.status_code = 200
    return response
