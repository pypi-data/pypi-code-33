
from dataclasses import dataclass, replace, field
from typing import Any, Callable, Iterable, List, Dict, Tuple

from .decorators import decoratormethod, decoratorlist
from .route import Route


@dataclass
class RoutingMixIn():
    """
    analogous to flask.Flask and flask.Blueprint combined
    """

    _application_changed: bool = True

    context: List[Callable] = field(default_factory=decoratorlist)

    routes: List[Route] = field(default_factory=list)

    def _add_route(self, route):
        self._application_changed = True
        self.routes.append(route)

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
            self._add_route(route)
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
            self._add_route(route)
