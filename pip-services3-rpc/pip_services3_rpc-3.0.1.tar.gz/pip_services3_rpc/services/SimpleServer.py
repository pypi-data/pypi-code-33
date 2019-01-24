# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.rest.SimpleServer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Simple WSGI web server with shutdown hook
    from http://stackoverflow.com/questions/11282218/bottle-web-framework-how-to-stop
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import time
from bottle import WSGIRefServer

class SimpleServer(WSGIRefServer):
    def run(self, app):
        from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
        from wsgiref.simple_server import make_server
        import socket

        class FixedHandler(WSGIRequestHandler):
            def address_string(self):
                return self.client_address[0]
            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls  = self.options.get('server_class', WSGIServer)

        if ':' in self.host:
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        srv = make_server(self.host, self.port, app, server_cls, handler_cls)
        self.srv = srv
        srv.serve_forever()

    def shutdown(self):
        attempts = 100
        while attempts > 0:
            if hasattr(self, 'srv'):
                try:
                    self.srv.shutdown()
                except:
                    pass
                break
            attempts -= 1
            time.sleep(0.1)
