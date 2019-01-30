#!/usr/bin/env python3.7

from dataclasses import dataclass, replace, field
from typing import Any, Callable, Iterable, List, Dict, Tuple
from pprint import pprint
from inspect import isgenerator, getfullargspec
from functools import partial, wraps
from itertools import chain

from more_itertools import collapse
from werkzeug.wrappers import Request, Response
from werkzeug.local import Local, LocalManager, LocalProxy, LocalStack
from werkzeug.exceptions import HTTPException, NotFound, Unauthorized, abort
from werkzeug.routing import Map, Rule
from werkzeug.utils import redirect
from werkzeug.serving import run_simple

from .decorators import decoratormethod, decoratorlist
from .exceptions import MissingContextVariable

__all__ = 'request', 'context', 'Madness', 'Response'

local = Local()
local_manager = LocalManager([local])
request = local('request')
context = local('context')



def bind_endpoint(endpoint, context_decorators):
    """binds the endpoint to the context
    """

    if not context_decorators:
        return endpoint

    def wrapped_endpoint():
        # run context before/after the endpoint
        # context may catch exceptions

        exitstack = []

        try:
            for func in context_decorators:
                gen = context.run(func)
                if isgenerator(gen):
                    try:
                        gen.send(None)
                    except StopIteration:
                        pass
                    else:
                        exitstack.append(gen)

            # if endpoint aborts, allow context to catch it!
            response = context.run(endpoint)

        except Exception as exception:
            # allow context to recover from an error
            current_exception = exception
            response = None
        else:
            current_exception = None

        #print('unstack', repr(current_exception), 'and', response)

        for gen in reversed(exitstack):
            try:
                if current_exception == None:
                    #print('send', response, 'into', gen)
                    new_response = gen.send(response)
                else:
                    #print('throw', repr(current_exception), 'into', gen)
                    new_response = gen.throw(current_exception)
            except StopIteration:
                pass
            except HTTPException as new_response:
                # abort()/raise used to create a new response
                # continue calling exception handlers
                current_exception = new_response
                response = None
            except Exception as exception:
                current_exception = exception
                response = None
            else:
                if new_response != None:
                    #print(gen, 'modified response', repr(response), 'type=', type(response))
                    current_exception = None
                    response = new_response

        if current_exception != None:
            raise current_exception

        return response

    return wrapped_endpoint



@dataclass
class Route():
    """
    path does not begin with a leading slash
    """
    path: str
    endpoint: Callable
    methods: List[str] = field(default_factory=list)
    context: List = field(default_factory=list)

    @property
    def rule(self) -> Rule:
        return Rule(
            f'/{self.path}',
            endpoint = bind_endpoint(self.endpoint, self.context_decorators),
            methods = self.methods or None
        )

    @property
    def context_decorators(self) -> Tuple:
        """
        """
        return tuple(collapse(self.context))

    def __repr__(self):
        context = ','.join([func.__qualname__ for func in self.context_decorators])
        if context:
            context = f'-> @({context})'
        methods = ','.join(self.methods)
        if methods:
            methods = f'[{methods}]'
        parts = ' '.join(
            filter(
            bool, (
            self.__class__.__name__,
            f'/{self.path}',
            methods,
            context,
            f'-> {self.endpoint.__qualname__}',
        )))
        return f'<{parts}>'



class Context(dict):

    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__

    def run(self, func):
        "pass kwargs directly from this context"
        kwargs = {}
        for key in getfullargspec(func).args:
            try:
                value = self[key]
            except KeyError:
                raise MissingContextVariable(key, func)
            else:
                kwargs[key] = value
        return func(**kwargs)




class HTTPMethodsMixIn():
    """convenience methods for .route()"""

    @decoratormethod
    def get(self, *args, **kwargs):
        return self.route(*args,  methods=['GET'], **kwargs)

    @decoratormethod
    def post(self, *args, **kwargs):
        return self.route(*args, methods=['POST'], **kwargs)

    @decoratormethod
    def put(self, *args, **kwargs):
        return self.route(*args, methods=['PUT'], **kwargs)

    @decoratormethod
    def delete(self, *args, **kwargs):
        return self.route(*args, methods=['DELETE'], **kwargs)

    @decoratormethod
    def patch(self, *args, **kwargs):
        return self.route(*args, methods=['PATCH'], **kwargs)

    @decoratormethod
    def options(self, *args, **kwargs):
        return self.route(*args, methods=['OPTIONS'], **kwargs)


class RESTFulRoutesMixIn(HTTPMethodsMixIn):
    """convenience methods for .route()

    https://medium.com/@shubhangirajagrawal/the-7-restful-routes-a8e84201f206
    https://gist.github.com/alexpchin/09939db6f81d654af06b
    """

    resource_id = '<int:id>'

    @decoratormethod
    def index(self, endpoint, *paths, **kwargs):
        "display a list of this resource"
        for path in paths or ['']:
            self.get(endpoint, f'{path}', **kwargs)
        return endpoint

    @decoratormethod
    def new(self, endpoint, *paths, **kwargs):
        "show a form to create this resource"
        for path in paths or ['']:
            self.get(endpoint, f'new{path}', **kwargs)
        return endpoint

    @decoratormethod
    def create(self, endpoint, *paths, **kwargs):
        "add a new resource to database, then redirect"
        for path in paths or ['']:
            self.post(endpoint, path, **kwargs)
        return endpoint

    @decoratormethod
    def show(self, endpoint, *paths, **kwargs):
        "show info about one resource"
        for path in paths or ['']:
            self.get(endpoint, f'/<int:id>{path}', **kwargs)
        return endpoint

    @decoratormethod
    def edit(self, endpoint, *paths, **kwargs):
        "show a form to edit one resource"
        for path in paths or ['']:
            self.get(endpoint, f'/<int:id>/edit{path}', **kwargs)
        return endpoint

    @decoratormethod
    def update(self, endpoint, *paths, **kwargs):
        "update a particular resource, then redirect"
        for path in paths or ['']:
             self.put(endpoint, f'/<int:id>{path}', **kwargs)
        return endpoint

    @decoratormethod
    def destroy(self, endpoint, *paths, **kwargs):
        "delete a particular resource, then redirect"
        for path in paths or ['']:
             self.delete(endpoint, f'/<int:id>{path}', **kwargs)
        return endpoint



class CORSMixIn():
    "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS"

    @decoratormethod
    def route(self, endpoint:Callable, *paths:Tuple[str], origin:Any=[], max_age:int=None, vary:str=None, methods:List[str]=[], headers:List[str]=None, **kwargs) -> Callable:
        """
        origin may be a list of urls or '*'
        headers is a whitelist of request headers
        default is to allow all headers
        """

        if 'OPTIONS' in methods:
            @wraps(endpoint)
            def wrapped_endpoint():
                if request.method == 'OPTIONS':

                    options_headers = {}

                    request_origin = request.environ.get('HTTP_ORIGIN', '*')

                    if request_origin in origin:
                        options_headers['Access-Control-Allow-Origin'] = request_origin
                        options_headers['Access-Control-Allow-Methods'] = ', '.join(methods)
                        if 'Access-Control-Request-Headers' in request.headers:
                            if headers == None:
                                allow_headers = request.headers['Access-Control-Request-Headers']
                            else:
                                allow_headers = ', '.join(headers)
                            options_headers['Access-Control-Allow-Headers'] = allow_headers

                    if vary:
                        options_headers['Vary'] = vary

                    if max_age != None:
                        options_headers['Access-Control-Max-Age'] = str(max_age)

                    return Response([], headers=options_headers)
                else:
                    return context.run(endpoint)
        else:
            wrapped_endpoint = endpoint

        super().route(wrapped_endpoint, *paths, methods=methods, **kwargs)
        return endpoint


@dataclass
class RoutingMixIn():
    """
    analogous to flask.Flask and flask.Blueprint combined
    """

    context: List[Callable] = field(default_factory=decoratorlist)

    routes: List[Route] = field(default_factory=list)

    def __iter__(self):
        yield from self.routes

    @decoratormethod
    def route(self, endpoint, *paths, methods=[], context=[]):

        for path in paths or [endpoint.__name__]:
            route = Route(
                path = path,
                endpoint = endpoint,
                methods = methods,
                context = [self.context, context],
            )
            self.routes.append(route)
        return endpoint

    def extend(self, routes: Iterable[Route], path='', context=True):
        """

        path should be empty or start with a slash

        e.g.
            api.extend(routes, '/v5')
        or
            versions.extend(routes, '/v5')
            api.extend(versions)

        if context is True, this context will wrap the routes

        """
        for route in routes:
            route = replace(route, path = path + route.path)
            if context:
                route = replace(route, context = [self.context, route.context])
            self.routes.append(route)




@dataclass
class Madness(CORSMixIn, RoutingMixIn, RESTFulRoutesMixIn):
    """the entrypoint
    """

    errors: Dict[int, Callable] = field(default_factory=dict)

    @decoratormethod
    def error(self, endpoint, status_code=None):
        """register an error handler e.g. 404
        should be used on the top level routes
        """
        self.errors[status_code] = endpoint
        return endpoint

    def callable(self, debug=False) -> Callable:
        """create a WSGI application
        see `uwsgi --callable`
        """

        routes = tuple(self)
        mapper = Map([route.rule for route in routes])

        errors = {
            code: bind_endpoint(endpoint, self.context)
            for code, endpoint in self.errors.items()
        }

        if debug:
            print('-'*10, 'routes', '-'*10)
            for route in routes:
                print(route)
            print('-'*28)
            pprint(errors)
            print('-'*28)

        @local_manager.make_middleware
        def wsgi_application(environ, start_response):
            global local, Request, response, Response
            nonlocal mapper, errors
            local.request = Request(environ)
            local.context = Context()
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

    def run(self, *, port=9090, host='127.0.0.1', debug=True):
        """run development server"""
        run_simple(
            host,
            port,
            self.callable(debug=debug),
            use_debugger = debug,
            use_reloader = debug
        )
