"""
    Copyright 2016 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""
import tempfile
import os
import shutil
import sys
import io
import logging
from distutils import dir_util


from inmanta import compiler
from inmanta import module
from inmanta import export
from inmanta import config
from inmanta import const
from inmanta.agent import cache
from inmanta.agent import handler
from inmanta.agent import io as agent_io
import pytest
from collections import defaultdict
import yaml


CURDIR = os.getcwd()
LOGGER = logging.getLogger()


option_to_env = {
    "inm_venv":"INMANTA_TEST_ENV",
    "inm_module_repo":"INMANTA_MODULE_REPO"
}

def pytest_addoption(parser):
    group = parser.getgroup(
        'inmanta', 'inmanta module testing plugin')
    group.addoption('--venv', dest='inm_venv',
                    help='folder in which to place the virtual env for tests (will be shared by all tests), overrides INMANTA_TEST_ENV')
    group.addoption('--module_repo', dest='inm_module_repo',
                    help='location to download modules from, overrides INMANTA_MODULE_REPO')

def get_opt_or_env_or(config, key, default):
    if config.getoption(key):
        return config.getoption(key)
    if option_to_env[key] in os.environ:
        return os.environ[option_to_env[key]]
    return default

def get_module_info():
    curdir = CURDIR
    # Make sure that we are executed in a module
    dir_path = curdir.split(os.path.sep)
    while not os.path.exists(os.path.join(os.path.join("/", *dir_path), "module.yml")) and len(dir_path) > 0:
        dir_path.pop()

    if len(dir_path) == 0:
        raise Exception("Module test case have to be saved in the module they are intended for. "
                        "%s not part of module path" % curdir)

    module_dir = os.path.join("/", *dir_path)
    with open("module.yml") as m:
        module_name = yaml.load(m)["name"]

    return module_dir, module_name


@pytest.fixture(scope="session")
def project(request):
    """
        A test fixture that creates a new inmanta project with the current module in. The returned object can be used
        to add files to the unittest module, compile a model and access the results, stdout and stderr.
    """
    _sys_path = sys.path
    test_project_dir = tempfile.mkdtemp()
    os.mkdir(os.path.join(test_project_dir, "libs"))

    repos = get_opt_or_env_or(request.config, "inm_module_repo", "https://github.com/inmanta/").split(" ")

    env_override = get_opt_or_env_or(request.config, "inm_venv", None)
    if env_override is not None:
        try:
            os.symlink(env_override, os.path.join(test_project_dir, ".env"))
        except OSError:
            LOGGER.exception(
                "Unable to use shared env (symlink creation from %s to %s failed).",
                env_override,
                os.path.join(test_project_dir, ".env")
            )
            raise

    with open(os.path.join(test_project_dir, "project.yml"), "w+") as fd:
        fd.write("""name: testcase
description: Project for testcase
repo: ['%(repo)s']
modulepath: libs
downloadpath: libs
""" % {"repo": "', '".join(repos)})

    # copy the current module in
    module_dir, module_name = get_module_info()
    dir_util.copy_tree(module_dir, os.path.join(test_project_dir, "libs", module_name))

    test_project = Project(test_project_dir)

    # create the unittest module
    test_project.create_module("unittest")

    yield test_project

    try:
        shutil.rmtree(test_project_dir)
    except PermissionError:
        LOGGER.warning(
            "Cannot cleanup test project %s. This can be caused because we try to remove a virtual environment, "
            "loaded by this python process. Try to use a shared environment with --venv", test_project_dir
        )

    sys.path = _sys_path


class MockAgent(object):
    """
        A mock agent for unit testing
    """
    def __init__(self, uri):
        self.uri = uri


class Project():
    """
        This class provides a TestCase class for creating module unit tests. It uses the current module and loads required
        modules from the provided repositories. Additional repositories can be provided by setting the INMANTA_MODULE_REPO
        environment variable. Repositories are separated with spaces.
    """
    def __init__(self, project_dir):
        self._test_project_dir = project_dir
        self._stdout = None
        self._stderr = None
        self._sys_path = None
        self.types = None
        self.version = None
        self.resources = {}
        self._exporter = None
        self._blobs = {}
        self._facts = defaultdict(dict)
        config.Config.load_config()

    def add_blob(self, key, content, allow_overwrite=True):
        """
            Add a blob identified with the hash of the content as key
        """
        if key in self._blobs and not allow_overwrite:
            raise Exception("Key %s already stored in blobs" % key)
        self._blobs[key] = content

    def stat_blob(self, key):
        return key in self._blobs

    def get_blob(self, key):
        return self._blobs[key]

    def add_fact(self, resource_id, name, value):
        self._facts[resource_id][name] = value

    def get_handler(self, resource, run_as_root):
        # TODO: if user is root, do not use remoting
        c = cache.AgentCache()
        if run_as_root:
            agent = MockAgent("ssh://root@localhost")
        else:
            agent = MockAgent("local:")

        c.open_version(resource.id.version)
        try:
            p = handler.Commander.get_provider(c, agent, resource)
            p.set_cache(c)
            p.get_file = lambda x: self.get_blob(x)
            p.stat_file = lambda x: self.stat_blob(x)
            p.upload_file = lambda x, y: self.add_blob(x, y)

            return p
        except Exception as e:
            raise e

        c.close_version(resource.id.version)

    def get_resource(self, resource_type: str, **filter_args: dict):
        """
            Get a resource of the given type and given filter on the resource attributes. If multiple resource match, the
            first one is returned. If none match, None is returned.
        """
        def apply_filter(resource):
            for arg, value in filter_args.items():
                if not hasattr(resource, arg):
                    return False

                if getattr(resource, arg) != value:
                    return False

            return True

        for resource in self.resources.values():
            if not resource.is_type(resource_type):
                continue

            if not apply_filter(resource):
                continue

            return resource

        return None

    def deploy(self, resource, dry_run=False, run_as_root=False):
        """
            Deploy the given resource with a handler
        """
        h = self.get_handler(resource, run_as_root)

        assert h is not None

        ctx = handler.HandlerContext(resource)
        h.execute(ctx, resource, False)

        return ctx

    def deploy_resource(self, resource_type: str, status=const.ResourceState.deployed, run_as_root=False, **filter_args: dict):
        res = self.get_resource(resource_type, **filter_args)
        assert res is not None, "No resource found of given type and filter args"

        ctx = self.deploy(res, run_as_root)
        if ctx.status != status:
            print("Deploy did not result in correct status")
            print("Requested changes: ", ctx._changes)
            for l in ctx.logs:
                print("Log: ", l._data["msg"])
                print("Kwargs: ", ["%s: %s" % (k, v) for k, v in l._data["kwargs"].items() if k != "traceback"])
                if "traceback" in l._data["kwargs"]:
                    print("Traceback:\n", l._data["kwargs"]["traceback"])

        assert ctx.status == status
        return res

    def io(self, run_as_root=False):
        version = 1
        if run_as_root:
            ret = agent_io.get_io(None, "ssh://root@localhost", version)
        else:
            ret = agent_io.get_io(None, "local:", version)
        return ret

    def create_module(self, name, initcf="", initpy=""):
        module_dir = os.path.join(self._test_project_dir, "libs", name)
        os.mkdir(module_dir)
        os.mkdir(os.path.join(module_dir, "model"))
        os.mkdir(os.path.join(module_dir, "files"))
        os.mkdir(os.path.join(module_dir, "templates"))
        os.mkdir(os.path.join(module_dir, "plugins"))

        with open(os.path.join(module_dir, "model", "_init.cf"), "w+") as fd:
            fd.write(initcf)

        with open(os.path.join(module_dir, "plugins", "__init__.py"), "w+") as fd:
            fd.write(initpy)

        with open(os.path.join(module_dir, "module.yml"), "w+") as fd:
            fd.write("""name: unittest
version: 0.1
license: Test License
            """)

    def compile(self, main):
        """
            Compile the configuration model in main. This method will load all required modules.
        """
        # write main.cf
        with open(os.path.join(self._test_project_dir, "main.cf"), "w+") as fd:
            fd.write(main)

        # compile the model
        test_project = module.Project(self._test_project_dir)
        module.Project.set(test_project)

        try:
            old_stdout = sys.stdout
            old_stderr = sys.stderr

            stdout = io.StringIO()
            stderr = io.StringIO()

            sys.stdout = stdout
            sys.stderr = stderr

            (types, scopes) = compiler.do_compile(refs={"facts": self._facts})

            exporter = export.Exporter()
            version, resources = exporter.run(types, scopes, no_commit=True)

            for key, blob in exporter._file_store.items():
                self.add_blob(key, blob)

            self.version = version
            self.resources = resources
            self.types = types
            self._exporter = exporter

            self._stdout = stdout.getvalue()
            self._stderr = stderr.getvalue()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def get_stdout(self):
        return self._stdout

    def get_stderr(self):
        return self._stderr

    def add_mock_file(self, subdir, name, content):
        """
            This method can be used to register mock templates or files in the virtual "unittest" module.
        """
        dir_name = os.path.join(self._test_project_dir, "libs", "unittest", subdir)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        with open(os.path.join(dir_name, name), "w+") as fd:
            fd.write(content)
