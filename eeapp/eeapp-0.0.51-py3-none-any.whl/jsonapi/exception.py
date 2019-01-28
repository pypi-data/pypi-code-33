__author__ = 'zhuxietong'
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from .response import ApiState


class EeException(APIException):
    def __init__(self, instance,line=None,file=None):
        super(EeException,self).__init__(instance)




def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)



    # Now add the HTTP status code to the response.
    if response is not None:
        response["Access-Control-Allow-Origin"] = " * "
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = " * "


        response.data['status'] = ApiState.exception.value
        response.data['data'] = None
        response.status_code = 200
    else:
        data = {}
        data['status'] = ApiState.exception.value
        data['data'] = None

        response["Access-Control-Allow-Origin"] = " * "
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = " * "

        response = Response(data=data, status=200, headers=None)

    return response
