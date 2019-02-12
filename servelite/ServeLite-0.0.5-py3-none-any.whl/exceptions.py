from flask import jsonify

def std_res(status_code, msg, **kwargs):
    res = {
        'code': status_code,
        'msg': msg,
    }
    for i in kwargs:
        res[i] = kwargs[i]
    return jsonify(res)

class WrongTypeInfoComment(Exception):
    def __init__(self, table, col=''):
        self.message = 'JSON info required in comment of {0}.{1}'.format(table, col)
        Exception.__init__(self, self.message)

class NoMatchedEndpoint(Exception):
    def __init__(self):
        self.message = 'Can not match an endpoint for the function. You may ignore @app.router()'
        Exception.__init__(self, self.message)

class payloadIllegalError(Exception):
    def __init__(self, err="illegal payload inside. Secrete key may have been disclosed!"):
        Exception.__init__(self, err)