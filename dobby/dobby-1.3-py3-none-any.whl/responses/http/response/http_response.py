class HttpResponse:
    def __init__(self, status_code, body):
        self.statusCode = status_code
        self.body = body
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        }

    def format(self):
        return {
            "statusCode": self.statusCode,
            "body": self.body or "",
            "headers": self.headers
        }
