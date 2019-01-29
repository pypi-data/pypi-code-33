import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.checks.registry import register
from django.db.backends.signals import connection_created
from django.core.management.color import color_style
from django.core.exceptions import ImproperlyConfigured

from .address import Address
from .system_checks import edc_base_check
from .utils import get_utcnow


style = color_style()


def activate_foreign_keys(sender, connection, **kwargs):
    """Enable integrity constraint with sqlite.
    """
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')


class AppConfig(DjangoAppConfig):
    name = 'edc_base'
    verbose_name = 'Edc Base'
    institution = 'Institution (see edc_base.AppConfig.institution)'
    project_name = 'Project Title (see edc_base.AppConfig.project_name)'
    project_repo = ''
    physical_address = Address()
    postal_address = Address()
    disclaimer = 'For research purposes only.'
    default_url_name = 'home_url'
    copyright = f'2010-{get_utcnow().year}'
    license = 'GNU GENERAL PUBLIC LICENSE Version 3'

    def ready(self):
        register(edc_base_check)
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        connection_created.connect(activate_foreign_keys)
        sys.stdout.write(
            f' * default TIME_ZONE {settings.TIME_ZONE}.\n')
        if not settings.USE_TZ:
            raise ImproperlyConfigured('EDC requires settings.USE_TZ = True')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
