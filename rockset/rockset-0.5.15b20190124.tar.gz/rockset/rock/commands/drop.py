from .command_auth import AuthCommand
from .util.type_util import TypeUtil
from docopt import docopt
from rockset.exception import InputError

class Drop(AuthCommand):
    def usage(self):
        return """
usage:
  rock drop --help
  rock drop [-h] --file=<YAMLFILE>
  rock drop <resource-type> <name> ...

arguments:
    <resource-type>          oneof collections or integrations.
    <name>                   name of the collection/integration to be dropped

Valid resource types:
  * collections (aka 'col')
  * integrations (aka 'int')

options:
    -f FILE, --file=FILE     drop all resources defined in the YAML file
    -h, --help               show this help message and exit
        """

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args))

        # handle file option
        fn = parsed_args['--file']
        if fn:
            parsed = self._parse_yaml_file(fn)
            self.set_batch_items('resource', parsed)
            return {}

        resource_type = TypeUtil.parse_resource_type(parsed_args['<resource-type>'])
        if resource_type is None:
            ret = 'Error: invalid resource type "{}"\n'.format(resource_type)
            ret += self.usage()
            raise SystemExit(ret.strip())

        if len(parsed_args['<name>']) > 1:
            resources = [{'name': n, 'type': resource_type} for n in parsed_args['<name>']]
            self.set_batch_items('resource', resources)
            return {}

        name = {'name': parsed_args['<name>'].pop()}
        return {"resource": {'type': resource_type, **name}}

    def go(self):
        self.logger.info('drop {}'.format(self.resource))
        if self.resource["type"] == TypeUtil.TYPE_COLLECTION:
            return self.go_collection()
        elif self.resource["type"] == TypeUtil.TYPE_INTEGRATION:
            return self.go_integration()
        else:
            return 1

    def go_collection(self):
        r = self.client.retrieve(name=self.resource['name'])
        r.drop()
        self.lprint(
            0, '{} "{}" was dropped successfully.'.format(
                r.type.capitalize(), r.name
            )
        )
        return 0

    def go_integration(self):
        i = self.client.Integration.retrieve(name=self.resource['name'])
        i.drop()
        self.lprint(
            0, '{} {} "{}" was dropped successfully.'.format(
            i.type,
            TypeUtil.TYPE_INTEGRATION.capitalize(), i.name
            )
        )
        return 0
