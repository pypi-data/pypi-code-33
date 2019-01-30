#
# copyright (c) 2019 east301
#
# This software is released under the Apache License, Version 2.0.
# https://opensource.org/licenses/Apache-2.0
#

from celery import current_app
from celery.bin.worker import worker
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        loglevel =['ERROR', 'WARNING', 'INFO', 'DEBUG'][kwargs['verbosity']]
        worker(app=current_app._get_current_object()).run(
            loglevel=loglevel,
            traceback=kwargs['traceback']
        )
