import json

class AckMessageBody(object):

    def __init__(self):
        self.id = ''
        self.code = ''
        self.data = dict()
        self.message = ''

    def encode(self):
        payload = dict()
        real_code = self.getCode()
        if(self.getCode() == ''):
            real_code = 0
        payload['code'] = real_code
        if(self.id is not None):
            payload['id'] = self.getId()
        if(self.data is not None):
            payload['data'] = self.getData()
        if(self.message is not None):
            payload['message'] = self.getMessage()
        return json.dumps(payload)

    def getId(self):
        if hasattr(self, 'id'):
            return self.id

    def setId(self, id):
        self.id = id

    def getCode(self):
        if hasattr(self, 'code'):
            return self.code

    def getData(self):
        if hasattr(self, 'data'):
            return self.data

    def setData(self, data):
        self.data = data

    def getMessage(self):
        if hasattr(self, 'message'):
            return self.message

    def setMessage(self, message):
        self.message = message

    def setCode(self, code):
        self.code = code