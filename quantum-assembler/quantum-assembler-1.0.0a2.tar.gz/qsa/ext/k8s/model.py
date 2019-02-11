import yaml
from ansible.plugins.filter.core import b64encode


class Secret:
    
    @property
    def base64(self):
        data = {}
        for key in self.data:
            data[key] = b64encode(self.data[key])
        return data

    def __init__(self, name, data, namespace=None):
        self.namespace = namespace
        self.name = name
        self.data = data

    def __str__(self):
        spec = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': self.name
            },
            'type': 'Opaque',
            'data': self.base64
        }
        return str.strip(yaml.safe_dump(spec, indent=2, default_flow_style=False))
