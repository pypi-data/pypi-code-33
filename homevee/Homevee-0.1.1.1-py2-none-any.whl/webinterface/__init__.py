#!/usr/bin/python
# -*- coding: utf-8 -*-
import SimpleHTTPServer
import SocketServer

import os

PORT = 8000

def start_http_server():
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

    httpd = SocketServer.TCPServer(("", PORT), Handler)

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    print "HTTP-Server running on port: "+str(8000)

    httpd.serve_forever()