#
# copyright (c) 2019 east301
#
# This software is released under the Apache License, Version 2.0.
# https://opensource.org/licenses/Apache-2.0
#

import os

from django.core.management import BaseCommand
from gunicorn.app.base import BaseApplication

from gpc_auth.wsgi import application


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-b', '--bind', default='127.0.0.1:8000')
        parser.add_argument('-w', '--workers', type=int, default=1)
        parser.add_argument('-s', '--script-name')

    def handle(self, *args, **kwargs):
        #
        if kwargs.get('script_name'):
            os.environ['SCRIPT_NAME'] = kwargs['script_name']

        #
        DjangoApplication(kwargs['bind'], kwargs['workers']).run()


class DjangoApplication(BaseApplication):
    def __init__(self, bind, workers):
        self._bind = bind
        self._workers = workers
        super().__init__()

    def load_config(self):
        self.cfg.set('bind', self._bind)
        self.cfg.set('workers', self._workers)

    def load(self):
        return application
