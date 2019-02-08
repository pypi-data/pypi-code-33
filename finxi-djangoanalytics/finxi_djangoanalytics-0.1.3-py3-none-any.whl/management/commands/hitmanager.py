from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Create an app with default template to use django-s3pooler'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str)

    def handle(self, *args, **options):
        try:
            call_command('startapp',
                         options['app_name'],
                         template='https://github.com/Corbelli/django_templates/archive/django_analytics.zip')
        except KeyError:
            raise CommandError('Missing app name')
        self.stdout.write(self.style.SUCCESS('Hit Manager App created!'))
