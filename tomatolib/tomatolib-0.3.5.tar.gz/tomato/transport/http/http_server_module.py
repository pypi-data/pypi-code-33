#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      http_server.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    tangmi(tangmi360@gmail.com)
    @date:      June 11, 2018
    @desc:      Basic http server functions and router rules encapsulation
"""

import json
import logging
from aiohttp import web
from tomato.transport.http import index_html
from tomato.util.appmodule import AppModule


class HttpServerModule(AppModule):

    def __init__(self, *args, **kwargs):
        super(HttpServerModule, self).__init__(*args, **kwargs)
        setting = kwargs.get('setting', None)
        if setting: kwargs.update(setting)
        self._host = args[0] if len(args) > 0 else kwargs.get('host', 'localhost')
        self._port = int(args[1] if len(args) > 1 else kwargs.get('port', '1024'))
        self._services = kwargs.get('services', [])

        self._app = web.Application()
        # self._app = web.Application(middlewares=[self.base_middleware,])
        self._app.router.add_route('get', '/', self.default_handler)
        for service in self._services:
            self._app.router.add_routes(service.routes)

    def setup(self):
        pass

    async def run(self):
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self._host, self._port)
        await site.start()
        logging.info('serving on [%s]', site.name)

    async def destroy(self):
        await self._runner.cleanup()
        await self._app.shutdown()
        await self._app.cleanup()

    async def close(self):
        await self.destroy()

    def default_handler(self, request):
        req_params = request.query
        response = web.Response(body=index_html.text.encode('utf-8'))
        response.headers['Content-Language'] = 'en'
        response.headers['Content-Type'] = 'en'
        return response

    @web.middleware
    async def base_middleware(self, request, handler):
        """http简单解包与封包
           1.qs信息从request.query属性中直接获取（MultiDictProxy类型）
           2.http body内容如果请求头为content_type=application/json,
             则通过json标准库进行解析，并覆盖request.body，
             否则直接把body内容抛到业务层自行处理（默认是byte类型）
           3.对于response的处理，目前简单判断为dict则直接转成json格式str发给调用端
             否则直接按业务层返回值返回给调用端
        """
        request.body = None
        if request.body_exists and request.can_read_body:
            request.body = await request.content.read()
            if request.content_type == 'application/json':
                try:
                    request.body = json.loads(request.body)
                except Exception as e:
                    logging.warning('json format warning, errmsg[%s]', str(e))
                    return web.json_response({'ret': 0, 'msg': 'params error'})
        logging.warning('type[%s]', type(handler))
        response = await handler(request)
        if isinstance(response, dict):
            return web.json_response(response)
        else:
            return web.Response(body=response)

        response = await handler(request)
        return response
