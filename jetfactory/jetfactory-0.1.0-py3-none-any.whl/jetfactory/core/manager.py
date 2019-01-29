# -*- coding: utf-8 -*-

import aiohttp
from os import getpid
from peewee import Model
from jetfactory.utils import format_path
from jetfactory.database import Database


class JetManager:
    pkgs = []
    sanic = None
    loop = None
    db = Database
    http_client: aiohttp.ClientSession

    @property
    def models(self) -> [str, Model]:
        for pkg_name, pkg in self.pkgs:
            for model in pkg.models:
                yield pkg, model

    def get_pkg(self, name):
        return dict(self.pkgs).get(name)

    def _load_packages(self, packages: list):
        for pkg in packages:
            if pkg.name in dict(self.pkgs).keys():
                raise Exception(f'Duplicate package name {pkg.name}')

            pkg.log.debug('Loading package')
            self.pkgs.append((pkg.name, pkg))

    def _register_services(self):
        for pkg_name, pkg in self.pkgs:
            [svc.register(pkg, self) for svc in pkg.services]

    def _register_models(self):
        models = list(self.models)
        registered = []

        if models and not self.db.connection:
            raise Exception('Unable to register models without a database connection')

        for pkg, model in models:
            if not hasattr(model, 'Meta'):
                meta = type('ModelMeta', (object, ), {})
                model.Meta = meta

            meta = model._meta
            meta.database = self.db.connection
            meta.table_name = f'{pkg.name}__{meta.table_name}'

            pkg.log.debug(f'Registering model: {model.__name__} [{meta.table_name}]')

            registered.append(model)

        with self.db.connection.allow_sync():
            self.db.connection.create_tables(registered, safe=True)

    async def _register_controllers(self):
        for pkg_name, pkg in self.pkgs:
            pkg.log.info('Controller initializing')
            path_base = self.sanic.config['API_BASE']
            pkg.controller.register(pkg)
            ctrl = pkg.controller = pkg.controller()

            for handler, route, schema in ctrl.pending_routes:
                handler_addr = hex(id(handler))
                handler_name = f'{pkg_name}.{route.name}'
                path_full = format_path(path_base, pkg.path, route.path)
                pkg.log.debug(
                    f'Registering route: {path_full} [{route.method}] => '
                    f'{route.name} [{handler_addr}]'
                )

                self.sanic.route(
                    uri=path_full,
                    methods=[route.method],
                    host=None,
                    strict_slashes=False,
                    stream=None,
                    version=None,
                    name=handler_name,
                )(handler)

                # Store information about active routes inside controller
                ctrl_route = (handler_name, (path_full, route, schema))
                ctrl.routes.append(ctrl_route)

            # await ctrl.on_ready()
            pkg.log.info('Controller initialized')

    async def detach(self, *_):
        await self.http_client.close()

    async def attach(self, app, loop):
        self._load_packages(app.packages)
        self.sanic = app
        self.loop = loop

        self.http_client = aiohttp.ClientSession(loop=loop)
        if app.config['DB_URL']:
            self.db.register(app, loop)
            self._register_models()

        self._register_services()
        await self._register_controllers()
        app.log.info(f'Worker {getpid()} ready for action')


jetmgr = JetManager()
