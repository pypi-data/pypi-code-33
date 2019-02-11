from qsa.ext.base import BaseExtension

from .schema import ConfigSchema


class Extension(BaseExtension):
    name = 'project'
    schema_class = ConfigSchema

    def on_project_init(self, quantum, typname, name, *args, **kwargs):
        self.spec = {
            'project': {
                'name': name,
                'type': typname
            }
        }
        if kwargs.get('language'):
            self.spec['project']['language'] = kwargs['language']
        quantum.update(self.spec)
