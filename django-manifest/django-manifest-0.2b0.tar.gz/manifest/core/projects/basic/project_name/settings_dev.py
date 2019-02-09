# -*- coding: utf-8 -*-
"""
Django local settings for {{ project_name }} project.
"""

import os
from . import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MIDDLEWARE = settings.MIDDLEWARE + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS = settings.INSTALLED_APPS + (
    'debug_toolbar',
)

# Settings for Django Debug Toolbar
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
#    'INTERCEPT_REDIRECTS': False,
#    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
#    'EXTRA_SIGNALS': ['{{ project_name }}.signals.MySignal'],
#    'HIDE_DJANGO_SQL': False,
#    'TAG': 'div',
#    'ENABLE_STACKTRACES' : True,
}

# The email backend to use.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Host for sending email.
# EMAIL_HOST = '' 
# EMAIL_PORT = 587

# SMTP Authentication
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
