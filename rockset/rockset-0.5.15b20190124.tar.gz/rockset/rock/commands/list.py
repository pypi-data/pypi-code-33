from docopt import docopt

from .command_rest import RESTCommand
from rockset.integration import Integration


class List(RESTCommand):
    @classmethod
    def what(cls):
        return ('ls', 'List all collections')

    def usage(self):
        return """
usage: rock ls [-h] [<resource-type>]

List all collections or integrations.

arguments:
    <resource-type>       oneof collections or integrations. Default: collections

Valid resource types:
  * collections (aka 'col')
  * integrations (aka 'int')

options:
  -h, --help            show this help message and exit
        """

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args, help=False))

        # handle help
        if parsed_args['--help']:
            ret = self.usage()
            raise SystemExit(ret.strip())

        resource_type = parsed_args['<resource-type>']

        # check if list integrations
        if resource_type in ['col', 'collection', 'collections']:
            return {'resource': 'COLLECTIONS'}
        elif resource_type in ['int', 'integration', 'integrations']:
            return {'resource': 'INTEGRATIONS'}
        elif resource_type is not None:
            ret = 'Error: invalid resource type "{}"\n'.format(resource_type)
            ret += self.usage()
            raise SystemExit(ret.strip())

        return {'resource': 'COLLECTIONS'}

    def go(self):
        if self.resource == 'INTEGRATIONS':
            return self.go_integrations()
        return self.go_collections()

    def go_collections(self):
        path = '/v1/orgs/{}/ws/{}/collections'.format('self', 'commons')
        items = self.get(path)['data']
        for item in items:
            item['type'] = 'COLLECTION'
        sorted_items = sorted(items, key=lambda k: k['type'] + ':' + k['name'])
        return (0, sorted_items)

    def go_integrations(self):
        path = '/v1/orgs/{}/integrations'.format('self')
        items = self.get(path)['data']
        for item in items:
            item['type'] = self.integration_type(item)
        sorted_items = sorted(items, key=lambda k: k['type'] + ':' + k['name'])
        return (0, sorted_items)

    def print_result(self, result):
        if self.resource == 'INTEGRATIONS':
            self.print_list(
                0, result, ['type', 'name', 'description', 'created_by']
            )
            return
        self.print_list(
            0, result, ['name', 'status', 'description', 'created_by']
        )

    def integration_type(self, integration):
        if integration['aws'] is not None:
            return Integration.TYPE_AWS
        elif integration['aws_external_id'] is not None:
            return Integration.TYPE_AWS_EXTERNAL_ID
        elif integration['gcp_service_account'] is not None:
            return Integration.TYPE_GCP_SERVICE_ACCOUNT
        else:
            return 'UNKNOWN'
