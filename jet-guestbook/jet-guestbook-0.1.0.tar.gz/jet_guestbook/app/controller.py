# -*- coding: utf-8 -*-

from jetfactory.controller import BaseController, Injector, route
from jetfactory.controller.decorators import schema
from .visit.schemas import Visit, Visits, VisitUpdate, VisitCreate, VisitCount, VisitDelete
from .visitor.schemas import Visitor, Visitors
from .visit import svc_visit
from .visitor import svc_visitor


class Controller(BaseController):
    def __init__(self):
        self.log.debug('Guestbook opening')

    async def on_ready(self):
        self.log.debug(f'Guestbook opened at {self.pkg.path}')

    async def on_request(self, request):
        self.log.debug(f'Request received: {request}')

    @route('/visitors', 'GET')
    @schema(Visitors)
    async def visitors_get(self, query):
        return await svc_visitor.get_many(query)

    @route('/visitors/<visitor_id>', 'GET')
    @schema(Visitor)
    async def visitor_get(self, visitor_id):
        return await svc_visitor.get_by_pk(visitor_id)

    @route('/visitors/<visitor_id>/visits', 'GET')
    @schema(Visits)
    async def visitor_entries(self, visitor_id, query):
        query.update({'visitor': visitor_id})
        return await svc_visit.get_many(**query)

    @route('/<visit_id>', 'GET')
    @schema(Visit)
    async def visit_get(self, visit_id):
        return await svc_visit.get_by_pk(visit_id)

    @route('/<visit_id>', 'PUT', inject=[Injector.remote_addr])
    @schema(VisitUpdate)
    async def visit_update(self, remote_addr, body, visit_id):
        return await svc_visit.visit_update(remote_addr, visit_id, body)

    @route('/<visit_id>', 'DELETE', inject=[Injector.remote_addr])
    @schema(VisitDelete)
    async def visit_delete(self, remote_addr, visit_id):
        return await svc_visit.visit_delete(remote_addr, visit_id)

    @route('/', 'GET')
    @schema(Visits)
    async def visits_get(self, query):
        return await svc_visit.get_many(**query)

    @route('/count', 'GET')
    @schema(VisitCount)
    async def visit_count(self, query):
        return {'count': await svc_visit.count(**query)}

    @route('/', 'POST', inject=[Injector.remote_addr])
    @schema(VisitCreate)
    async def visit_add(self, remote_addr, body):
        return await svc_visit.visit_add(remote_addr, body)
