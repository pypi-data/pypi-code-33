class JsonResult():
    '''
    JsonResult:

        >>> from eggit.api_response import JsonResult
        >>> result = JsonResult().get_dict()
        >>> result
        {'status': False}
        >>> result = JsonResult('some msg', True, 'some data', 100000)
        >>> result
        <eggit.api_response.JsonResult object at 0x7f8a7ac096a0>
        >>> result.get_dict()
        {'status': True, 'msg': 'some msg', 'data': 'some data', 'error_code': 100000}
    '''
    def __init__(self, msg=None, status=False, data=None, error_code=None):
        self._msg = msg
        self._status = status
        self._data = data
        self._error_code = error_code

    def get_dict(self):
        result = dict(status=self._status)

        if self._msg:
            result['msg'] = self._msg

        if self._data:
            result['data'] = self._data

        if self._error_code:
            result['error_code'] = self._error_code

        return result
