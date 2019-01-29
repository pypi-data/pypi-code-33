# -*- coding: utf-8 -*-

import peewee
from aiohttp import ClientSession as HTTPClientSession
from peewee_async import Manager
from jetfactory.exceptions import JetfactoryException
from jetfactory.core.component import BaseComponent


class VanillaService(BaseComponent):
    sanic = None
    loop = None
    db_manager = None
    http_client = None

    def register(self, pkg, mgr):
        if issubclass(self.__class__, DatabaseService):
            self.db_manager = mgr.db.manager

        if issubclass(self.__class__, HttpService):
            self.http_client = mgr.http_client

        self.loop = mgr.loop
        self.sanic = mgr.sanic
        self._pkg_bind(pkg)


class HttpService(VanillaService):
    http_client: HTTPClientSession

    async def http_request(self, *args, **kwargs):
        async with self.http_client.request(*args, **kwargs) as resp:
            result = await resp.json()
            return result, resp.status

    async def http_post(self, url, payload):
        return await self.http_request('POST', url, data=payload)

    async def http_get(self, url):
        return await self.http_request('GET', url)


class DatabaseService(VanillaService):
    __model__: peewee.Model
    db_manager: Manager

    @property
    def model(self):
        if not self.__model__:
            raise Exception(f'{self.__class__.__name__}.__model__ not set, unable to perform database operation')

        return self.__model__

    def select(self, *fields):
        return self.model.extended(*fields) if hasattr(self.model, 'extended') else self.model.select(*fields)

    def _model_has_attrs(self, *attrs):
        for attr in attrs:
            if not hasattr(self.model, attr):
                raise JetfactoryException(f'Unknown field {attr}', 400)

        return True

    def _parse_sortstr(self, value):
        if not value:
            return []

        model = self.model

        for col_name in value.split(','):
            sort_asc = True
            if col_name.startswith('-'):
                col_name = col_name[1:]
                sort_asc = False

            if self._model_has_attrs(col_name):
                sort_obj = getattr(model, col_name)
                yield sort_obj.asc() if sort_asc else sort_obj.desc()

    def _get_query_filtered(self, expression=None, select=None, **params):
        query_base = select or self.select()

        sort = params.pop('_sort', None)
        limit = params.pop('_limit', 0)
        offset = params.pop('_offset', 0)

        query = query_base.limit(limit).offset(offset)

        if isinstance(expression, peewee.Expression):
            query = query.where(expression)
        elif params:
            query = query.filter(**params)

        if sort:
            order = self._parse_sortstr(params['sort'])
            return query.order_by(*order)

        return query

    async def get_many(self, *args, **kwargs):
        query = self._get_query_filtered(*args, **kwargs)
        return [o for o in await self.db_manager.execute(query)]

    async def get_by_pk(self, record_id):
        return await self.get_one(self.__model__.id == record_id)

    async def create(self, item):
        return await self.db_manager.create(self.model, **item)

    async def get_or_create(self, item):
        return await self.db_manager.get_or_create(self.model, **item)

    async def count(self, *args, **kwargs):
        query = self._get_query_filtered(*args, **kwargs)
        return await self.db_manager.count(query)

    async def get_one(self, *args, **kwargs):
        query = self._get_query_filtered(*args, **kwargs)

        try:
            return await self.db_manager.get(query)
        except peewee.DoesNotExist:
            raise JetfactoryException('No such record', 404)

    async def update(self, record, payload):
        if not isinstance(record, peewee.Model):
            record = await self.get_by_pk(record)

        for k, v in payload.items():
            setattr(record, k, v)

        await self.db_manager.update(record)
        return record

    async def delete(self, record_id):
        record = await self.get_by_pk(record_id)
        deleted = await self.db_manager.delete(record)
        return {'deleted': deleted}
