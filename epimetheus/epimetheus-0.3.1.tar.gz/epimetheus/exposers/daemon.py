"""
NOTE: exposition of this webserver into public may be insecure
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler


class MetricRequestHandler(SimpleHTTPRequestHandler):
    pass


def run(addr: str, port: int):
    httpd = HTTPServer((addr, port), MetricRequestHandler)
    httpd.serve_forever()
