from qsa.ext.base import BaseExtension

from .model import Secret


class Extension(BaseExtension):
    name = 'k8s'
    command_name = 'k8s'
    subcommands = [
        {
            'name': 'secrets',
            'args': [
                {'dest': 'vault'}
            ]
        }
    ]

    def handle_secrets(self, args, vaults):
        """Open the vault specified in the command-line arguments and
        create Kubernetes ``Secret`` objects.
        """
        vault = vaults.get(args.vault)
        for i, item in enumerate(vault):
            name, spec = item
            secret = Secret(name, spec.data)
            if i > 0:
                print('\n')
            print('---')
            print(secret)
