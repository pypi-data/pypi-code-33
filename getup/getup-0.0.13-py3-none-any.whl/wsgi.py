
import os
from .up import configure_django

from .conf import Configuration

print('HELLOO', os.environ.get('GETUP_CONF_PATH'))

configure_django()

from django.conf import settings

print(vars(settings))

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
