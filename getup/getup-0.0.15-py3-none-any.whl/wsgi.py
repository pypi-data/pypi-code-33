
import os
from .up import configure_django

from .conf import Configuration

configure_django()

from django.conf import settings

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
