from pkg_resources import get_distribution
from pkg_resources import resource_filename
import logging
import logging.config
import pprint
from appdirs import AppDirs
import os
from dautil import conf


def env_logger(func_name):
    env_val = os.environ.get('DAUTIL_LOGGER')
    log_enabled = False

    if env_val:
        if env_val == '*':
            log_enabled = True
        elif func_name in env_val:
            log_enabled = True

    logger = conf_logger(func_name)

    if not log_enabled:
        logger.addHandler(logging.NullHandler())
        # Needed for ipython notebook sessions
        logger.propagate = False

    return logger



def get_logger(name):
    log_config = resource_filename(__name__, 'log.conf')
    logging.config.fileConfig(log_config)
    logger = logging.getLogger(name)

    return logger


def conf_logger(name):
    # TODO check for conf file in appropriate dir
    conf_file = 'dautil_log.conf'

    if conf.file_exists(conf_file):
        logging.config.fileConfig(conf_file, disable_existing_loggers=False)
    else:
        logging.basicConfig()

    return logging.getLogger(name)


def shorten(module_name):
    dot_i = module_name.find('.')

    return module_name[:dot_i]


def log(modules, name):
    skiplist = ['pkg_resources', 'distutils', 'zmq']

    logger = get_logger(name)
    logger.debug('Inside the log function')
    versions = {}

    for k in modules.keys():
        str_k = str(k)

        if '.version' in str_k:
            short = shorten(str_k)

            if short in skiplist:
                continue

            try:
                ver = get_distribution(short).version
                logger.info('%s=%s' % (short, ver))
                versions[short] = ver
            except ImportError:
                logger.warn('Could not import', short)

    return versions


class VersionsLogFileHandler(logging.FileHandler):
    def __init__(self, fName):
        dirs = AppDirs("PythonDataAnalysisCookbook", "Ivan Idris")
        path = dirs.user_log_dir
        print(path)

        if not os.path.exists(path):
            os.mkdir(path)

        super(VersionsLogFileHandler, self).__init__(
              os.path.join(path, fName))


class Printer():
    def __init__(self, modules=None, name=None):
        if modules and name:
            log(modules, name)

    def print(self, *args):
        for arg in args:
            pprint.pprint(arg)

        print()
