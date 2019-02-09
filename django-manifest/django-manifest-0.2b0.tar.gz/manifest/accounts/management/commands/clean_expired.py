# -*- coding: utf-8 -*-
try:
    from django.core.management.base import NoArgsCommand as BaseCommand
except ImportError:
    from django.core.management.base import BaseCommand
    
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    """
    Search for users that still haven't verified their email after
    ``ACCOUNTS_ACTIVATION_DAYS`` and delete them.

    """
    help = 'Deletes expired users.'
    def handle(self, *args, **options):
        users = get_user_model().objects.delete_expired_users()
