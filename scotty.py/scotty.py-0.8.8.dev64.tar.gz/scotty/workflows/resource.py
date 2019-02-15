import logging
import shutil
import os
from string import Template

from scotty.workflows.base import Workflow
from scotty.core.components import Resource
from scotty.core.exceptions import ScottyException
from scotty.core.workspace import Workspace

logger = logging.getLogger(__name__)


class ResourceInitWorkflow(Workflow):
    def _prepare(self):
        self.template_path = os.path.dirname(os.path.realpath(__file__))
        self.template_path = os.path.join(self.template_path, '../../templates/resource')
        self.resource_name = self._options.name
        self.resource = Resource()
        self.resource.workspace = Workspace.factory(self.resource, self.resource_name.lower())
        self.resource_module_path = self.get_module_path()
        self.resource_samples_path = os.path.join(self.resource.workspace.path, 'examples')
        self.resource_tests_path = os.path.join(self.resource_module_path, 'tests')
        self._check_existing_resource()

    def get_module_path(self):
        resource_workspace_path = self.resource.workspace.path
        resource_name_lower = self.resource_name.lower()
        return os.path.join(resource_workspace_path, resource_name_lower)

    def _check_existing_resource(self):
        if os.path.isfile(self.resource.module_path):
            msg = 'Destination {} is already an existing resource'
            raise ScottyException(msg.format(self.resource.workspace.path))

    def _run(self):
        start_resource_creation_msg = 'Start to create structure for resource (dir: {})'
        logger.info(start_resource_creation_msg.format(self.resource.workspace.path))
        self._create_dirs()
        self._create_module()
        self._create_resource_gen()
        self._create_examples()
        self._create_tests()
        self._create_readme()
        self._create_gitignore()

    def _create_dirs(self):
        functional_tests_path = os.path.join(self.resource_tests_path, 'functional')
        self._ensure_dir(self.resource.workspace.path)
        self._ensure_dir(self.resource_module_path, True)
        self._ensure_dir(self.resource_samples_path)
        self._ensure_dir(self.resource_tests_path, True)
        self._ensure_dir(functional_tests_path, True)

    def _ensure_dir(self, path, package=False):
        if not os.path.isdir(path):
            os.mkdir(path)
        if package:
            package_mark_file = os.path.join(path, '__init__.py')
            with open(package_mark_file, 'w'):
                pass

    def _create_file_from_tpl(self, tpl_path, target_path, placeholder_values):
        with open(tpl_path, 'r') as tpl_file:
            tpl_content = Template(tpl_file.read()).safe_substitute(placeholder_values)
        with open(target_path, 'w') as target_file:
            target_file.write(tpl_content)

    def _create_module(self):
        resource_submodule_path = os.path.join(self.resource_module_path, 'resource.py')
        resource_submodule_tpl_path = os.path.join(self.template_path, 'resource.py.tpl')
        params = {"resource_class_name": self.resource_class_name}
        self._create_file_from_tpl(resource_submodule_tpl_path, resource_submodule_path, params)

    def _create_resource_gen(self):
        resource_gen_path = self.resource.module_path
        resource_gen_tpl_path = os.path.join(self.template_path, 'resource_gen.py.tpl')
        resource_name = self.resource_name
        resource_var = resource_name[0].lower() + resource_name[1:]
        params = {
            "resource_module_name": self.resource_module_name,
            "resource_class_name": self.resource_class_name,
            "resource_object_name": self.resource_object_name
        }
        self._create_file_from_tpl(resource_gen_tpl_path, resource_gen_path, params)

    @property
    def resource_module_name(self):
        resource_module_name = self.resource_name.lower()
        return resource_module_name

    @property
    def resource_class_name(self):
        resource_class_name = self.resource_name
        resource_class_name = resource_class_name[0].upper() + resource_class_name[1:]
        resource_class_name = resource_class_name + 'Resource'
        return resource_class_name

    @property
    def resource_object_name(self):
        resource_object_name = self.resource_name
        resource_object_name = resource_object_name[0].lower() + resource_object_name[1:]
        return resource_object_name

    def _create_examples(self):
        experiment_yaml_path = os.path.join(self.resource_samples_path, 'experiment.yaml')
        experiment_yaml_tpl_path = os.path.join(self.template_path, 'experiment.yaml.tpl')
        params = {"resource_object_name": self.resource_name.lower()}
        self._create_file_from_tpl(experiment_yaml_tpl_path, experiment_yaml_path, params)

    def _create_tests(self):
        tox_file_tpl = os.path.join(self.template_path, 'tox.ini.tpl')
        tox_file = os.path.join(self.resource.workspace.path, 'tox.ini')
        params = {"resource_module_name": self.resource_module_name}
        self._create_file_from_tpl(tox_file_tpl, tox_file, params)
        test_case_tpl = os.path.join(self.template_path, 'test_experiment_perform.py.tpl')
        test_case_file = os.path.join(
            self.resource_tests_path,
            'functional',
            'test_experiment_perform.py'
        )
        params = {
            "resource_name": self.resource_module_name,
            "function_name": self.resource_module_name
        }
        self._create_file_from_tpl(test_case_tpl, test_case_file, params)

    def _create_readme(self):
        readme_md = os.path.join(self.resource.workspace.path, 'README.md')
        readme_md_tpl = os.path.join(self.template_path, 'README.md.tpl')
        shutil.copyfile(readme_md_tpl, readme_md)

    def _create_gitignore(self):
        gitignore = os.path.join(self.resource.workspace.path, '.gitignore')
        gitignore_tpl = os.path.join(self.template_path, '.gitignore.tpl')
        shutil.copyfile(gitignore_tpl, gitignore)

    def _clean(self):
        pass
