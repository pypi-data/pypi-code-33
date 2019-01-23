#!/usr/bin/env python3
"""
HTTP server for metrics
"""

import traceback
from urllib.parse import urlparse
from urllib import parse
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from . import collector


class EsSearchExporterHandler(BaseHTTPRequestHandler):
    def __init__(self, config, kerberos, tls, *args, **kwargs):
        self._config = config
        self._kerberos = kerberos
        self._tls = tls
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):
        config = self._config
        url = urlparse(self.path)
        if url.path == '/esdata':
            params = parse.parse_qs(parse.unquote(self.path.split('?', 1)[1]))
            if 'search' not in params:
                self.send_response(400)
                self.end_headers()
                msg = "Missing 'search' from parameters %s" % params['searcdh']
                self.wfile.write(msg.encode())
                return
            search = params['search'][0]
            if search not in config['searches']:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(
                    "Search {} not found in config".format(search).encode())
                return
            try:
                output = collector.search_es(
                    config['searches'][search], self._kerberos, self._tls)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(output)
            except:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(traceback.format_exc().encode())
        elif url.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"""<html>
      <head><title>Elasticsearch Data Exporter</title></head>
      <body>
      <h1>Elasticsearch Data Exporter</h1>
      <p>Visit <code>/metrics?search=example</code> to use.</p>
      </body>
      </html>""")
        else:
            self.send_response(404)
            self.end_headers()


def start_http_server(config, port, kerberos, tls):
    GetHandler = lambda *args, **kwargs: EsSearchExporterHandler(
        config, kerberos, tls, *args, **kwargs)
    server = HTTPServer(('', port), GetHandler)
    print('Starting server, use <Ctrl-C> to stop\n', config)
    server.serve_forever()
