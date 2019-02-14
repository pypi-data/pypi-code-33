import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from django_saml2_framework.models import IdentityProvider, ServiceProvider

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('--idp',
            # action='store_true',
            # dest='delete',
            help='IdP EntityID',)
        parser.add_argument('--sp',
            # action='store_true',
            # dest='delete',
            help='SP EntityID',)
        parser.add_argument('--create',
            action='store_true',
            # dest='create',
            help='Create the Provider if it is not found.')
        # parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        if not (bool(options['idp']) != bool(options['sp'])):
            self.stdout.write(self.style.ERROR('You must have either --idp or --sp'))
            return
        
        if options['idp']:
            entity_id = options['idp']
            Provider = IdentityProvider
        if options['sp']:
            entity_id = options['sp']
            Provider = ServiceProvider
        provider = None
        try:
            provider = Provider.objects.get(entity=entity_id)
        except Provider.DoesNotExist:
            if options['create']:
                provider = Provider(entity=entity_id, name=entity_id)
                self.stdout.write('Creating new provider.')
            else:
                self.stdout.write(self.style.ERROR('The provider {} does not exists in the system.'.format(entity_id)))
                self.stdout.write(self.style.ERROR('Add --create to have it created for you.'))
                return
        
        

        # subprocess.check_call(['openssl', 'genrsa', '-out', '/tmp/server.key', '1024'])
        # # subprocess.check_call(['chmod 600 /tmp/server.key'])
        # subprocess.check_call(['openssl', 'req', '-new', '-key', '/tmp/server.key', '-out', '/tmp/server.csr'])
        # subprocess.check_call(['openssl', 'x509', '-req', '-days 365', '-in /tmp/server.csr', '-signkey /tmp/server.key', '-out /tmp/server.crt'],
        #                       env={'RANDFILE':'/tmp/.rnd'})
        # proc.wait()
        subprocess.check_call(['openssl', 'req', '-x509', '-nodes', '-newkey', 'rsa:2048', '-keyout', '/tmp/server.key', '-out', '/tmp/server.crt', '-days', '365'],
                              env={'RANDFILE':'/tmp/.rnd'})
        self.stdout.write(self.style.SUCCESS('Created new key.'))
        
        with open('/tmp/server.crt') as f:
            provider.cert_file.save(entity_id + '.crt', File(f), save=False)
        with open('/tmp/server.key') as f:
            provider.key_file.save(entity_id + '.key', File(f), save=False)

        provider.save()
        self.stdout.write(self.style.SUCCESS('Provider Saved!'))
