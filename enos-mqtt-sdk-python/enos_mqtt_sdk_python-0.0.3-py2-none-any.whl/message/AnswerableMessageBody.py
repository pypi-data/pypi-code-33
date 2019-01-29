import json

class AnswerableMessageBody(object):

    def __init__(self):
        self.id = ''
        self.method = ''
        self.version = ''
        self.params = dict()

    def encode(self):
        payload = dict()
        if self.getId() is not None:
            payload['id'] = self.getId()
        if self.getVersion() is not None:
            payload['version'] = self.getVersion()
        if self.getMethod() is not None:
            payload['method'] = self.getMethod()
        if self.getParams() is not None:
            payload['params'] = self.params
        return json.dumps(payload)

    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id

    def getMethod(self):
        return self.method

    def setMethod(self, method):
        self.method = method

    def getVersion(self):
        return self.version

    def setVersion(self, version):
        self.version = version

    def getParams(self):
        return self.params

    def setParams(self, params):
        self.params = params

    def toString(self):
        return 'AnswerableMessageBody{' + 'id=' + self
        id1 + '\'' + ',method=' + self.method + '\'' + ', version=' + self.version + '\'' + ',params=' + self.params + '}'