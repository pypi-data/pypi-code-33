import os
from django.conf import settings
from django.apps import apps

skel_dir = os.path.join(os.path.dirname(__file__), 'skel')

class Factory:
    """Rest_framework_factory Factory class"""

    def __init__(self):
        self._init_skel()
        self._init_api()

    def create_from_scratch(self, model_name=None, model_qualified_name=None):
        """Create a new DRF API, model and all. """
        skel_names = ['imports', 'model', 'serializer', 'filter', 'form', 'viewset', 'router', 'register', 'urlpatterns']
        content = self._generate_api_content(
            model_name=model_name,
            model_qualified_name=model_qualified_name,
            skel_names=skel_names)
        return content

    def build_from_model(self, app_name=None, model_name=None, self_contained=False, copy_model=False):
        """Build a DRF API from an existing django model
        The model name should be given as it appears in models.py ie it should be Upper case
        """
        skel_names = ['serializer', 'filter', 'form', 'viewset', 'register']

        if self_contained:
            skel_names = ['imports', 'router'] + skel_names + ['urlpatterns', ]

        if copy_model:
            pass
            #TODO: include the model code itself in the api

        app_config = self._get_app_or_die(app_name=app_name)
        model_class = self._get_model_or_die(app_name=app_name, model_name=model_name)
        model_name = model_class.__name__
        model_qualified_name = "{0}.{1}".format(model_class.__module__, model_class.__name__)  # ie app0.models.MyModel

        # we know we have a valid model, for now all we do is build the api string.
        content = '#{0}\n#==== drff api for {1} =====\n#{0}\n'.format('='*10, model_name)
        content += self._generate_api_content(
            model_name=model_name, model_qualified_name=model_qualified_name,  skel_names=skel_names
            )
        api_id = "{0}.{1}".format(app_name, model_name)
        self.apis['model'][api_id] = content
        return content

    def build_from_app(self, app_name=None, model_list='__all__'):
        """Build a DRF API for all or a subset of the models in a django app"""
        app = self._get_app_or_die(app_name)

        content = ''
        #prliminary content
        content += "import {0}.models\n".format(app_name)
        skel_names = ['imports', 'router', ]

        for skel_name in skel_names:
            content += self._read_skel(skel_name)

        #model content
        if model_list == '__all__':
            models = [x for x in app.get_models()]
        else:
            models = []
            for m in model_list:
                try:
                    models.append(app.get_model(model_name=m))
                except LookupError:
                    raise ValueError("Model named {0} does not exist".format(m))
        for model in models:
            model_name = model._meta.object_name
            content += self.build_from_model(app_name=app_name, model_name=model_name)

        #ending content
        skel_names = ['urlpatterns']
        for skel_name in skel_names:
            content += self._read_skel(skel_name)
        self.apis['app'][app_name] = content

    def _get_app_or_die(self, app_name=None):
        """Return the app from django.apps.app_configs[app_name] or die trying"""
        if app_name is None:
            raise ValueError("App name is required")
        try:
            app = apps.app_configs[app_name]
            return app
        except KeyError:
            print('An app named {0} does not exist or is not registered with Django'.format(app_name))
            raise

    def _get_model_or_die(self, app_name=None, model_name=None):
        """Return the model from app_configs[app_name].get_model[model_name] or die trying"""
        if not model_name:
            raise ValueError("A model name is required")
        app = self._get_app_or_die(app_name)
        try:
            model = app.get_model(model_name)
            return model
        except KeyError:
            print("Model named {0} not found in app {1}".format(model_name, app_name))
            raise

    def _read_skel(self, skel_name=None):
        """Read a skel file"""
        if skel_name is None:
            raise ValueError("Skel name required")

        skel_file = os.path.join(skel_dir, skel_name + '.py.txt')
        try:
            with open(skel_file) as f:
                return f.read()
        except Exception:
            print("Error reading skel file {0}".format(skel_file))
            raise

    def _generate_api_content(self,
                              model_name=None,
                              model_qualified_name=None,
                              skel_names=()):
        if not model_name:
            raise ValueError("Model name required")
        if not model_qualified_name:
            raise ValueError("Model qualified name required")
        if not skel_names:
            raise ValueError("List of skel files cannot be empty")
        content = ''
        for skel_name in skel_names:
            skel_content = self._read_skel(skel_name)
            content += skel_content.format(
                model_name=model_name,
                model_qualified_name=model_qualified_name,
                model_name_lcase=model_name.lower())
        return content

    def _init_skel(self):
        self.skel = {}
        for fn in os.listdir(skel_dir):
            key = fn.split('.')[0]
            with open(os.path.join(skel_dir, fn)) as fh:
                self.skel[key] = fh.read()

    def _init_api(self):
        self.apis = {}
        self.apis['model'] = {}
        self.apis['app'] = {}
        self.apis['test'] = {}
        self.apis['test']['TestModel'] = self.create_from_scratch(
            model_name='TestModel',
            model_qualified_name='testapp.models.TestModel'
        )

    def _write_to_file(self):
        pass

