
from functools import wraps

from .decorators import decoratormethod

class ApplicationAsRouteMixIn():
    "allows routing to WSGI applications"

    @decoratormethod
    def error(self, endpoint, status_code, wsgi=False):
        super().error(status_code)(lambda:endpoint if wsgi else endpoint)
        return endpoint

    @decoratormethod
    def route(self, endpoint, *args, wsgi=False, **kwargs):
        if wsgi:
            for path in args:
                self._mount(endpoint, path)
        else:
            super().route(*args, **kwargs)(endpoint)
        return endpoint

    def _mount(self, application, path):
        @self.route(path, path + '/<path:mount>')
        @wraps(application)
        def application_endpoint():
            def proxy_response(environ, start_response):
                environ['PATH_INFO'] = environ['PATH_INFO'].replace(f'/{path}', '/', 1)
                print('@mount', environ['PATH_INFO'])
                return application(environ, start_response)
            return proxy_response
        return application
