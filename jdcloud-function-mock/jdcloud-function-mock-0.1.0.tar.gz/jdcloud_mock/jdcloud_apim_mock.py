#coding=utf-8

import http.server
import socketserver
import datetime
import uuid
from urllib.parse import urlparse, parse_qs

__all__ = ['run']

handlers = [None]

class ApimHttpHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        return self.do_Method('GET')

    def do_POST(self):
        return self.do_Method('POST')

    def do_Method(self, method):
        """Serve a request."""
        event = {
            "version": "0",
            "id": "6a7e8feb-b491-4cf7-a9f1-bf3703467718",
            "time": "2006-01-02T15:04:05.999999999Z",
            "base64OwnerPin": "NTk0MDM1MjYzMDE5",
            "resources": ["jrn:apigateway:cn-north-1::api/function"],
            "region": "cn-north-1",
            "detailType": "ApiGatewayReceived",
            "detail": {
                "path": "api request path",
                "headers": {
                    "x-jdcloud-request-id": "headerValue"
                },
                "pathParameters": {
                },
                "queryParameters": {
                },
                "body": "string of request payload",
                "requestContext": {
                    "stage": "test",
                    "apiId": "testsvc",
                    "identity": {
                        "accountId": "",
                        "apiKey": "",
                        "authType": ""
                    },
                    "sourceIp": "127.0.0.1"
                }
            }
        }
        event["time"] = '{0:%Y-%m-%dT%H:%M:%S.%f000Z}'.format(datetime.datetime.now(datetime.timezone.utc))
        event["detail"]["httpMethod"] = method
        print(list(self.headers))
        for k in self.headers:
            event["detail"]["headers"][k.lower()] = self.headers[k]
        reqid = str(uuid.uuid4())
        event["detail"]["headers"]["x-jdcloud-request-id"] = reqid
        event["detail"]["headers"]["j-forwarded-for"] = "127.0.0.1"
        event["detail"]["headers"]["x-forwarded-for"] = "127.0.0.1"
        event["detail"]["headers"]["x-proto"] = "HTTP"
        event["detail"]["requestContext"]["requestId"] = reqid

        o = urlparse(self.path)
        q = parse_qs(o.query, keep_blank_values=True)

        event["detail"]["path"] = o.path
        for qk in q:
            v = q[qk]
            for i in range(len(v)):
                if v[i] == "":
                    v[i] = True
            if len(v) == 1:
                event["detail"]["queryParameters"][qk] = v[0]
            else:
                event["detail"]["queryParameters"][qk] = v
        res = handlers[0](event, None)
        self.send_response(res['statusCode'])
        for k, v in res['headers'].items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(res['body'].encode('utf8'))
        return str(res)

class Mock(object):
    def __init__(self):
        pass

    def _parse_server_address(self, server_address):
        if server_address is None:
            return ('127.0.0.1', 8080)
        if type(server_address) is str:
            words = server_address.split(':', 1)
            return (words[0], int(words[1]))
        if type(server_address) is tuple:
            if len(server_address) == 2:
                return (str(server_address[0]), int(server_address[1]))
        raise TypeError

    def run(self, handler, server_address=None):
        handlers[0] = handler
        server_address = self._parse_server_address(server_address)

        with socketserver.TCPServer(server_address, ApimHttpHandler) as httpd:
            print("serving at %s", server_address)
            httpd.serve_forever()

def run(handler, port):
    mock = Mock()
    mock.run(handler, port)