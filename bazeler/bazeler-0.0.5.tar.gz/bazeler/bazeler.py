#!/usr/bin/env python
'''
Bazeler: A bazel management tool. This writes WORKSPACE files for each
module/repository that has {requires,provides}.json files defined in the root.
'''

import distutils.spawn
from os import path, listdir, linesep
import json
import platform
import pkg_resources
import subprocess
from collections import  OrderedDict
import logging
from jinja2 import Template

VERBOSE = False
OS = platform.system()
ARCH = platform.machine()

assert (pkg_resources.resource_exists(__name__, 'data'))
DATA_PATH = pkg_resources.resource_filename(__name__, 'data')

assert (pkg_resources.resource_exists(__name__, 'data/precompiled'))
PRECOMPILED_PATH = pkg_resources.resource_filename(__name__, 'data/precompiled')

assert (pkg_resources.resource_exists(__name__, 'data/buildfiles'))
BUILDFILE_PATH = pkg_resources.resource_filename(__name__, 'data/buildfiles')

assert (pkg_resources.resource_exists(__name__, 'data/installs'))
INSTALLS_PATH = pkg_resources.resource_filename(__name__, 'data/installs')

assert (pkg_resources.resource_exists(__name__, 'data/defaults'))
DEFAULTS_PATH = pkg_resources.resource_filename(__name__, 'data/defaults')

assert (pkg_resources.resource_exists(__name__, 'data/fragments'))
FRAGMENTS_PATH = pkg_resources.resource_filename(__name__, 'data/fragments')

assert (pkg_resources.resource_exists(__name__, 'data/BUILD'))
BUILD = pkg_resources.resource_filename(__name__, 'data/BUILD')

LOCAL_REPOSITORY_TEMPLATE = r'''local_repository(
        name = "{}",
        path = "{}"
)
'''

NEW_LOCAL_REPOSITORY_TEMPLATE = r'''new_local_repository(
        name = "{}",
        path = "{}",
        build_file_content = """{}"""
)
'''

def __executable_exists(executable):
    return distutils.spawn.find_executable(executable)

def __has_gpu():
    if 'Darwin' == OS:
        return False
    QUERY = 'lshw'
    assert __executable_exists(QUERY)
    CMD = [QUERY, '-C',  'display']
    process = subprocess.Popen(CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = process.communicate()
    return out.count('NVIDIA') > 0

def __get_system_root():
    if OS == "Linux":
        return "/usr"
    elif OS == "Darwin":
        return "/usr/local"
    else:
        raise RuntimeError('Unsupported OS: [{}]'.format(OS))

class Status:
    OK = 0
    WARNING = 1
    ERROR = 2
    UNKNOWN = 3

def __is_installed_list(meta):
    contents = meta['contents']
    for content in contents:
        if not path.isfile(content):
            return (Status.ERROR, '[{}] : could not find {}'.format(meta['name'], content))
    return (Status.OK, 'Success')

def __is_installed_glob(meta):
    import glob
    for expression in meta['expressions']:
        contents = glob.glob(expression)
        if len(contents) > 0:
            return (Status.OK, 'Success')
    return (Status.ERROR, 'Failed to glob: [{}]'.format(meta['expressions']))

def __is_installed_dpkg(meta):
    tool = 'dpkg'
    assert __executable_exists(tool)
    name = meta['name']
    CMD = [tool, '-s', name]
    process = subprocess.Popen(CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, _ = process.communicate()
    if process.returncode == 0:
        return (Status.OK, 'Success')
    return (Status.ERROR, '[{}] not installed. Try: sudo apt-get install {}'.format(name, name))

def __is_installed_brew(meta):
    tool = 'brew'
    assert __executable_exists(tool) is not None
    name = meta['name']
    CMD = [tool, 'list', name]
    process = subprocess.Popen(CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, _ = process.communicate()
    if process.returncode == 0:
        return (Status.OK, 'Success')
    return (Status.ERROR, '[{}] not installed. Try: brew install {}'.format(name, name))

    return process.returncode == 0

def __is_installed_default(*args, **kwargs):
    return (Status.OK, 'Local installation')

def __is_not_available(*args, **kwags):
    strict = False
    if strict:
        return (Status.ERROR, 'Not available on this platform')
    return (Status.WARNING, 'Not available on this platform : Build may fail!')

INSTALLATION_VALIDATIONS = {
    'dpkg': __is_installed_dpkg,
    'list': __is_installed_list,
    'glob': __is_installed_glob,
    'brew': __is_installed_brew,
    'yes': __is_installed_default,
    'no': __is_not_available
}

def __is_installed(name):
    META = path.join(INSTALLS_PATH, '{}.install'.format(name))
    if not path.isfile(META):
        return (Status.UNKNOWN, 'Installation status could not be determined')

    with open(META, 'r') as handle:
        logging.debug(META)
        meta = json.load(handle)[OS][ARCH]
    return INSTALLATION_VALIDATIONS[meta['tool']](meta)

def __load(directory, suffix='.fragment', build_file=True):
    if not path.isdir(directory):
        return {}
    fragments = [path.join(directory, file) for file in listdir(directory) if file.endswith(suffix)]
    manifests = {}
    for fragment in fragments:
        name, _ = path.splitext(path.basename(fragment))
        with open(fragment, 'r') as handle:
            template = Template(handle.read())
            if build_file:
                BUILD = path.join(BUILDFILE_PATH, OS, ARCH, '{}.BUILD'.format(name))
                if not path.exists(BUILD):
                    manifests[name] = (template, None, __get_system_root())
                else:
                    manifests[name] = (template, BUILD, __get_system_root())
            else:
                manifests[name] = (template, None, __get_system_root())
    return manifests

def defaults(offline=False):
    defaults = __load(DEFAULTS_PATH, build_file=False)
    if offline:
        load = __load(path.join(DEFAULTS_PATH, 'local'), build_file=False)
    else:
        load = __load(path.join(DEFAULTS_PATH, 'remote'), build_file=False)
    defaults.update(load)
    return defaults

def fragments(offline=False):
    fragments = __load(FRAGMENTS_PATH)
    if offline:
        load = __load(path.join(FRAGMENTS_PATH, 'local'))
    else:
        load = __load(path.join(FRAGMENTS_PATH, 'remote'))
    fragments.update(load)
    return fragments

def sources(root):
    ARGS = ['find', root, '-type', 'f', '-name', 'provides.json']
    finder = subprocess.Popen(ARGS, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = finder.communicate()
    files = stdout.strip().splitlines()
    manifests = {}
    for file in files:
        with open(file, 'r') as handle:
            entry = json.load(handle)
            manifests[entry['name']] = LOCAL_REPOSITORY_TEMPLATE.format(entry['name'], path.abspath(path.dirname(file)))
    return manifests

def precompiled():
    PRECOMPILED = path.join(PRECOMPILED_PATH, OS, ARCH)
    if not path.isdir(PRECOMPILED):
        return {}
    libraries = __load(PRECOMPILED, build_file=False)
    if __has_gpu():
        libraries.update(__load(path.join(PRECOMPILED, 'gpu'), build_file=False))
    else:
        libraries.update(__load(path.join(PRECOMPILED, 'non.gpu'), build_file=False))
    return libraries

def sinks(root):
    # Using `find` vs os.walk() is signifcantly faster.
    args = ['find', root, '-type', 'f', '-name', 'requires.json']
    finder = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = finder.communicate()
    return stdout.strip().splitlines()

def write(target, manifests, permissive=False):
    assert target
    logging.info('Target: {}'.format(target))
    with open(target, 'r') as handle:
        payload = handle.read()
    try:
        dependencies = json.loads(payload)['dependencies']
    except ValueError:
        if len(payload) == 0:
            # Empty file - no dependencies
            dependencies = []
        else:
            logging.error('Failed to decode [{}]'.format(target))
            return

    graph = OrderedDict()
    for dependency in dependencies:
        try:
            graph[dependency] = manifests[dependency]
        except:
            message = 'Mising dependency for [{}]. Tried to add [{}], which was not found in any manifest.'.format(target, dependency)
            if permissive:
                logging.error(message)
                continue
            else:
                raise RuntimeError(message)

    with open(path.join(path.dirname(target), 'WORKSPACE'), 'w') as handle:
        bazilla = LOCAL_REPOSITORY_TEMPLATE
        bazilla = bazilla.format('bazilla', DATA_PATH)
        handle.write(bazilla)
        handle.write(linesep)
        for name, data in graph.iteritems():
            handle.write('{}#-----------{}-----------{}'.format(linesep, name, linesep))
            if isinstance(data, tuple):
                template = data[0]
                build_file = data[1]
                system_root = data[2]
                if build_file:
                    status, note = __is_installed(name)
                    if status == Status.OK:
                        logging.info('{} : {}'.format(name, note))
                    elif status == Status.WARNING:
                        logging.warning('{} : {}'.format(name, note))
                    else:
                        logging.fatal('{} : {}'.format(name, note))
                handle.write(template.render(build_file=build_file, system_root=system_root))
            else:
                handle.write(data)

def execute(root, offline=False, search_paths=None, use_precompiled=False, verbose=False, permissive=False):
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    manifests = OrderedDict()
    manifests.update(defaults(offline))
    manifests.update(fragments(offline))
    if use_precompiled:
        manifests.update(precompiled())
    manifests.update(sources(root))

    if (search_paths):
        for search_path in search_paths.split(','):
            manifests.update(sources(search_path))

    outputs = sinks(root)
    if not outputs:
        logging.error('No packages analyzed under [{}]'.format(root))
        return 1
    for sink in outputs:
        write(sink, manifests, permissive)
