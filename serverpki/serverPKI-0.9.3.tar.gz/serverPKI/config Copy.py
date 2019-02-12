import importlib.util
import sys
from tokenize import tokenize

# name of our config module
CONFIG_MODULE = 'config'

# place where to find it (sys.prefix point at venve if we are in a venv)
CONFIG_MODULE_DIRS =(   sys.prefix + '/etc',
                        '/usr/local/etc/serverPKI')

print(__file__)

# https://docs.python.org/3/library/importlib.html#importlib.machinery.ModuleSpec
config_module = None
spec = importlib.util.spec_from_file_location(  tokenize.CONFIG_MODULE, 
                                                tokenize.CONFIG_MODULE_DIRS[0])
print(spec)
try:
    config_module = importlib.util.module_from_spec(spec)
except (AttributeError):
    spec = importlib.util.spec_from_file_location(  tokenize.CONFIG_MODULE,
                                                    tokenize.CONFIG_MODULE_DIRS[1])
    print(spec)
    try:
        config_module = importlib.util.module_from_spec(spec)
    except (AttributeError):
        print('?No config file in {} or {}'.format(
                        CONFIG_MODULE_DIRS[0], CONFIG_MODULE_DIRS[1]))
        sys.exit(1)
spec.loader.exec_module(config_module)

print(config.Pathes())
print(config.X509atts())
