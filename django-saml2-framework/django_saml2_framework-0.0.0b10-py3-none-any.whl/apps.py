from django.apps.config import AppConfig
from saml2.server import Server
from django.db.utils import OperationalError


class Saml2Config(AppConfig):
    name = 'django_saml2_framework'
    verbose_name = 'SAML2 Framework'

    def ready(self):
        pass
        # from django_saml2_framework.models import IdentityProvider
        # try:
        #     for idp in IdentityProvider.objects.all():
        #         idp.reload()
        # except OperationalError:
        #     pass
