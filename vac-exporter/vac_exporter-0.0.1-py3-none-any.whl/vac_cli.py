"""
VAC exporter for the Prometheus monitoring system.
"""

import os
import sys
from argparse import ArgumentParser
from vac_exporter.vac_http import start_http_server

def main(argv=None):
    """
    Main entry point.
    """

    parser = ArgumentParser(description='VAC metrics exporter for Prometheus')
    parser.add_argument('-c', '--config', dest='config_file',
                        default=None, help="configuration file")
    parser.add_argument('-p', '--port', dest='port', type=int,
                        default=9273, help="HTTP port to expose metrics")

    args = parser.parse_args(argv or sys.argv[1:])

    config = {
            'default': {
                'vac_user': os.environ.get('VAC_USER'),
                'vac_password': os.environ.get('VAC_PASSWORD'),
                'ignore_ssl': os.environ.get('VAC_IGNORE_SSL', False),
            }
        }

    for key in os.environ.keys():
        if key == 'VAC_USER':
            continue
        if not key.startswith('VAC_') or not key.endswith('_USER'):
            continue

        section = key.split('_', 1)[1].rsplit('_', 1)[0]

        config[section.lower()] = {
            'vac_user': os.environ.get('VAC_{}_USER'.format(section)),
            'vac_password': os.environ.get('VAC_{}_PASSWORD'.format(section)),
            'ignore_ssl': os.environ.get('VAC_{}_IGNORE_SSL'.format(section), False),
        }

    section = config.get(b'section', [b'default'])[0].decode('utf-8')
    if section not in config.keys():
        log("{} is not a valid section, using default".format(section))
        section = 'default'

    start_http_server(section, config[section].get('vac_user'), config[section].get('vac_password'), config[section].get('ignore_ssl'), args.port)
