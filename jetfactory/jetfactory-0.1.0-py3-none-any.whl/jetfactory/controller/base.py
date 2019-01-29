# -*- coding: utf-8 -*-

from jetfactory.core.component import BaseComponent
from .registry import ROUTES_PENDING, REQUEST_SCHEMAS


class BaseController(BaseComponent):
    routes = []

    @classmethod
    def register(cls, pkg):
        cls._pkg_bind(pkg)

    async def on_ready(self):
        pass

    async def on_request(self, *args):
        pass

    @property
    def pending_routes(self):
        return self._register_decorators()

    def _register_decorators(self):
        for member in self.__class__.__dict__.values():
            mid = id(member)

            if mid not in ROUTES_PENDING:
                # Not a route handler, skip
                continue

            # Claim pending route
            route = ROUTES_PENDING.pop(mid)
            handler = getattr(self, route.name)

            yield handler, route, REQUEST_SCHEMAS.pop(mid, None)

    def __repr__(self):
        return f'<{self.__class__.__name__} at {hex(id(self))}>'
