# Copyright 2017-2018 Purism SPC
# SPDX-License-Identifier: AGPL-3.0-or-later

# Original file from Celery 4.0.2 documentation
# Copyright 2009-2016 Ask Solem
# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
# SPDX-License-Identifier: CC-BY-SA-4.0

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'middleware.settings')

app = Celery('purist_middleware_monitor')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
