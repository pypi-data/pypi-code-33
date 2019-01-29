# -*- coding: utf-8 -*-

from jetfactory.service import DatabaseService
from jetfactory.exceptions import JetfactoryException
from .models import VisitModel
from ..visitor import svc_visitor


class VisitService(DatabaseService):
    __model__ = VisitModel
    VISITS_MAX = 10

    async def get_authored(self, visit_id, remote_addr):
        visit = await self.get_by_pk(visit_id)
        if visit.visitor.ip_addr != remote_addr:
            raise JetfactoryException('Not allowed from your IP', 403)

        return visit

    async def visit_count(self, ip_addr):
        return await self.count(VisitModel.visitor.ip_addr == ip_addr)

    async def visit_delete(self, remote_addr, visit_id):
        visit = await self.get_authored(visit_id, remote_addr)
        return await self.delete(visit.id)

    async def visit_update(self, remote_addr, visit_id, payload):
        visit = await self.get_authored(visit_id, remote_addr)
        return await self.update(visit, payload)

    async def visit_add(self, remote_addr, visit_new):
        visited = await self.visit_count(remote_addr)

        if visited >= self.VISITS_MAX:
            raise JetfactoryException(f'Max {self.VISITS_MAX} entries per IP. Try deleting some old ones.', 400)

        async with self.db_manager.transaction():
            city, country = await svc_visitor.ipaddr_location(remote_addr)
            visitor = dict(
                name=visit_new.pop('name'),
                ip_addr=remote_addr,
                location=f'{city}, {country}'
            )

            visit_new['visitor'], created = await svc_visitor.get_or_create(visitor)
            if created:
                self.log.info(f"New visitor: {visit_new['visitor'].name}")

            visit = await self.create(visit_new)
            self.log.info(f'New guestbook visit: {visit.id}')

        return visit
