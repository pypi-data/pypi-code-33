import os, sys, re
from envparse import env

BASE_DIR = env.str('BASE_DIR')
SAFE_DELETION = env.bool('SAFE_DELETION', default=True)
PLUGIN_NAME = env.str('PLUGIN_NAME', default='wolphin-driver')

if not os.path.isdir(BASE_DIR):
    err = '{} directory is set as base directory, but it doesn\'t exist'.format(BASE_DIR)
    sys.exit(err)

if not os.access(BASE_DIR, os.W_OK):
    err = 'No write permission for base directory {}'.format(BASE_DIR)
    sys.exit(err)

plugin_name_regexp = re.compile('^[A-Za-z0-9][A-Za-z0-9\_\-]{0,30}$')

if not plugin_name_regexp.match(PLUGIN_NAME):
    err = 'Wrong plugin name: {}'.format(PLUGIN_NAME)
    sys.exit(err)

