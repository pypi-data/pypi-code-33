import os
import sys
import shutil
from ne import Host
from ne import Container
from os.path import expanduser

root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
data = os.path.join(root, 'data')
HOME = expanduser("~")
DEFAULT_CONFIGURATION_PATH = os.path.join(HOME, ".ndocker")


def set_loglevel():
    import logging
    logger = logging.getLogger('ndocker')
    if len(logger.handlers) != 0:
        logger.setLevel(logging.DEBUG)


def create_host_cfg(filename, dest):
    if not filename.endswith('.yaml'):
        filename = '{}.yaml'.format(filename)

    _create_configration(filename, 'host', dest)


def create_container_cfg(container, device, dest):
    if len(container) > 5:
        print "The length of container name too long, should be <= 5."
        sys.exit(1)

    filename = '{}_EDITTHISPART.yaml'.format(container)
    _create_configration(filename, device, dest)


def _create_configration(filename, ne_type, dest):
    if ne_type not in [f[:-5] for f in os.listdir(data) if os.path.isfile(os.path.join(data, f))]:
        print 'Unsupport device: {}'.format(ne_type)
        sys.exit(1)

    if dest is None:
        dest = DEFAULT_CONFIGURATION_PATH
    subdir = 'containers' if ne_type != 'host' else 'host'
    dest = os.path.join(dest, subdir)
    if not os.path.exists(dest):
        os.makedirs(dest)

    template = os.path.join(data, '{}.yaml'.format(ne_type))
    dest = os.path.join(dest, filename)
    shutil.copy(template, dest)
    print "Create configration file at: {}".format(dest)


def _verify_host_cfg(func):
    def wrapper(filename, path):
        if path is None:
            path = DEFAULT_CONFIGURATION_PATH

        if not filename.endswith('.yaml'):
            filename = '{}.yaml'.format(filename)

        filename = os.path.join(path, 'host', filename)
        if not os.path.exists(filename):
            print "Configuration file doesn't exist at {}".format(filename)
            sys.exit(1)

        func(filename, path)
    return wrapper


@_verify_host_cfg
def config_host(filename, path):
    host = Host(filename)
    host.create_networks()


@_verify_host_cfg
def reset_host(filename, path):
    host = Host(filename)
    host.reset_networks()


def _get_container_cfg(container, path):
    if path is None:
        path = DEFAULT_CONFIGURATION_PATH

    subdir = os.path.join(path, 'containers')
    if not os.path.exists(subdir):
        print "Path doesn't exist: {}".format(subdir)
        sys.exit(1)

    cfg = None
    for filename in (f for f in os.listdir(subdir) if os.path.isfile(os.path.join(subdir, f))):
        if container in filename:
            cfg = filename
            break

    if cfg is None:
        print "Configuration file doesn't exist at {}".format(cfg)
        sys.exit(1)

    cfg = os.path.join(subdir, cfg)
    if not os.path.exists(cfg):
        print "Configuration file doesn't exist at {}".format(cfg)
        sys.exit(1)

    return cfg


def start_container(container, path):
    cfg = _get_container_cfg(container, path)
    ndocker = Container(cfg)
    ndocker.start_service()


def stop_container(container, path):
    cfg = _get_container_cfg(container, path)
    ndocker = Container(cfg)
    ndocker.stop_service()


def restart_container(container, path):
    cfg = _get_container_cfg(container, path)
    ndocker = Container(cfg)
    ndocker.restart_service()


def rm_container(container, path):
    cfg = _get_container_cfg(container, path)
    ndocker = Container(cfg)
    ndocker.rm_service()


def up_containers(path):
    if path is None:
        path = DEFAULT_CONFIGURATION_PATH

    subdir = os.path.join(path, 'containers')
    if not os.path.exists(subdir):
        print "Path doesn't exist: {}".format(subdir)
        sys.exit(1)

    for filename in (f for f in os.listdir(subdir) if os.path.isfile(os.path.join(subdir, f))):
        if not filename.endswith(".yaml"):
            logger.error("skip the {}.".format(filename))
            continue

        ndocker = Container(os.path.join(subdir, filename))
        ndocker.restart_service()
