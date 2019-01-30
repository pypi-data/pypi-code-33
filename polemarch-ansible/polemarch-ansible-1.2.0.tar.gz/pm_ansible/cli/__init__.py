import os
import sys


def update_warnings(value='false'):
    default_warnings = [
        'ANSIBLE_ACTION_WARNINGS',
        'ANSIBLE_SYSTEM_WARNINGS',
        'ANSIBLE_DEPRECATION_WARNINGS',
        'ANSIBLE_LOCALHOST_WARNING',
        'ANSIBLE_COMMAND_WARNINGS',
    ]
    for var_name in default_warnings:
        os.environ[var_name] = value


def main(args=sys.argv):
    if args[1] == 'reference':
        update_warnings()
        from . import reference
        reference.handler(args[2:])
    elif args[1] == 'modules':
        update_warnings()
        from . import modules
        modules.handler(args[2:])
    elif args[1] == 'inventory_parser':
        update_warnings()
        from . import inventory_parser
        inventory_parser.handler(args[2:])
    elif args[1] == 'config':
        update_warnings()
        from . import config
        config.handler(args[2:])
    else:
        from . import execute
        execute.handler(args[1:])
