from typing import Dict, Callable
from dataclasses import dataclass, field
from pprint import pprint

from werkzeug.wrappers import Request
from werkzeug.exceptions import HTTPException#, NotFound, Unauthorized, abort
from werkzeug.routing import Map
from werkzeug.serving import run_simple

from .decorators import decoratormethod
from .context import *

from .routing import RoutingMixIn

@dataclass
class ApplicationMixIn(RoutingMixIn):

    _application = None

    errors: Dict[int, Callable] = field(default_factory=dict)

    @decoratormethod
    def error(self, endpoint, status_code=None):
        """register an error handler e.g. 404
        should be used on the top level routes
        """
        self.errors[status_code] = endpoint
        return endpoint

    def get_application(self, debug:bool=False) -> Callable:

        mapper = Map([route.rule for route in self])

        errors = {
            code: bind(endpoint, self.context)
            for code, endpoint in self.errors.items()
        }

        if debug:
            print('-'*10, 'routes', '-'*10)
            for route in self:
                print(route)
            print('-'*28)
            pprint(errors)
            print('-'*28)

        @local_manager.make_middleware
        def wsgi_application(environ, start_response):
            global local, Request
            nonlocal mapper, errors
            local.request = Request(environ)
            local.context = Context(debug=debug)
            adapter = mapper.bind_to_environ(environ)
            try:
                endpoint, kwargs = adapter.match()
            except HTTPException as response:
                try:
                    endpoint = errors[response.code]
                except:
                    try:
                        endpoint = errors[None]
                    except KeyError:
                        return response(environ, start_response)
                response = endpoint()
                return response(environ, start_response)
            else:
                try:
                    # add path parameters to context
                    context.update(kwargs)
                    response = context.run(endpoint)
                    return response(environ, start_response)
                except HTTPException as response:
                    return response(environ, start_response)

        return wsgi_application

    def __call__(self, environ, start_response):
        """the WSGI application"""
        if self._application_changed:
            self._application = self.get_application()
            self._application_changed = False
        return self._application(environ, start_response)

    def run(self, *, port=9090, host='127.0.0.1', debug=True):
        """run development server"""
        run_simple(
            host,
            port,
            self.get_application(debug=debug),
            use_debugger = debug,
            use_reloader = debug
        )
