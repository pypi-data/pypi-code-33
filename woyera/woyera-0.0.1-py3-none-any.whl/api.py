import requests
import json

class Clean:

    def __init__(self):
        self.accessKey = None
        self.secretKey = None
        self.url = "http://127.0.0.1:8080/api/clean/"
        self.r = None

    def keys(self, accessKey, secretKey):
        self.accessKey = accessKey
        self.secretKey = secretKey

    def data(self, data, cleanClasses, columnNames=None, apply=None, analyze=None, dataFormat=None):
        data = {'data': data, 'cleanClasses': cleanClasses}

        request_body = self.add_to_request_body(data, columnNames, apply, analyze, dataFormat)

        r = requests.post(self.url, json=json.loads(json.dumps(request_body)),
                          headers={'accessKey': self.accessKey, 'secretKey': self.secretKey})

        self.r = r

        return r

    def add_to_request_body(self, data, columnNames, apply, analyze, dataFormat):
        if columnNames is not None:
            data['columnNames'] = columnNames

        if apply is not None:
            data['apply'] = apply

        if analyze is not None:
            data['analyze'] = analyze

        if dataFormat is not None:
            data['dataFormat'] = dataFormat

        return data