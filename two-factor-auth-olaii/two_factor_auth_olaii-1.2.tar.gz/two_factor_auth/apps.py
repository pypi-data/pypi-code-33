from __future__ import unicode_literals

from django.conf import settings
from django.apps import AppConfig


class TwoFactorAuthConfig(AppConfig):
    name = 'two_factor_auth'
    verbose_name = "Django Two Factor Authentication"

    def ready(self):
        from .admin import patch_admin
        if getattr(settings, 'TWO_FACTOR_PATCH_ADMIN', True):
            patch_admin()