from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import io
import types

class Server(BaseHTTPRequestHandler):
    __name__ = "Server"
    lastCommand = ""

    def do_GET(self):

        self.send_response(200)
        self.send_header('content-type', 'text/json')
        self.end_headers()

        tmpCommandDict = {'movement': Server.lastCommand}
        self.wfile.write(json.dumps(tmpCommandDict).encode("utf-8"))

    def do_POST(self):
        # Request the data length
        length = int(self.headers['Content-Length'])

        data = self.rfile.read(length).decode("utf-8")
        jsonData = json.loads(data)

        self.send_response(200)
        self.send_header('content-type', 'text/json')
        self.end_headers()
       
        Server.lastCommand = jsonData['movement']

def startServer():
    httpd = HTTPServer(('', 8080), Server)
    httpd.serve_forever()
        
if __name__ == "__main__":
    startServer()

    