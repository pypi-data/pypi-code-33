from django.core.management.base import BaseCommand

from ...site import site_reference_configs


class Command(BaseCommand):

    help = "Validates the reference model config"

    def handle(self, *args, **options):
        site_reference_configs.validate()
