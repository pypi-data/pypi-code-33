
import os

from .up import import_app
import_app()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
