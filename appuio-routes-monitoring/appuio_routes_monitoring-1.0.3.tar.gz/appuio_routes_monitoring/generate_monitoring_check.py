#!/usr/bin/python3

""" script to generate hieradata http monitoring check from appuio routes"""

import argparse
import subprocess
import logging
import yaml

LOG = logging.getLogger(__name__)


def get_routes(cmd):
    """get routes from APPUiO and return them as yaml"""

    try:
        rval = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        LOG.debug(
            'command "%s" completed with exit code "0" and output: "%s"',
            ' '.join(cmd),
            rval.strip().replace('\n', '; '),
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            'command "%s" failed with exit code "%s" and output: "%s"' % (
                ' '.join(cmd),
                exc.returncode,
                exc.output.strip().replace('\n', '; '),
            )
        ) from None
    try:
        return yaml.load(rval)['items']
    except yaml.YAMLError as exc:
        exit('Could not parse routes: %s' % exc)


def main():
    """ Generate hieradata code from APPUiO routes"""

    parser = argparse.ArgumentParser(
        description='generate hieradata from appuio routes',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog='appuio_routes_monitoring',
    )
    parser.add_argument(
        '-p', '--project', nargs='+',
        dest='projects', default='all'
    )
    parser.add_argument(
        '-k', '--key',
        dest='hierakey', default='profile_icinga2::hiera_httpchecks'
    )

    args = parser.parse_args()

    routes = []
    if args.projects == 'all':
        cmd = ['oc', 'get', 'routes', '-o', 'yaml', '--all-namespaces']
        routes = get_routes(cmd)

    else:
        for project in args.projects:
            cmd = ['oc', '-n', project, 'get', 'routes', '-o', 'yaml']
            routes += get_routes(cmd)

    hieradata = {}
    for route in routes:
        alert_customer = False
        production_level = None
        if 'annotations' in route['metadata']:
            annotations = route['metadata']['annotations']
            if 'monitoring/alert_customer' in annotations and \
                    annotations['monitoring/alert_customer'] != 'false':
                alert_customer = annotations['monitoring/alert_customer']
            if 'monitoring/alert_vshn' in annotations and \
                    annotations['monitoring/alert_vshn'] == 'true':
                production_level = 4

        hieradata[route['spec']['host']] = {
            'display_name': '%s on APPUiO in %s' % (route['spec']['host'],
                                                    route['metadata']['namespace']),
            'http_address': route['spec']['host'],
            'http_ssl': True,
            'vars': {
                'alert_customer': alert_customer
            }
        }
        if production_level:
            hieradata[route['spec']['host']]['production_level'] = production_level
        if 'tls' not in route['spec']:
            hieradata[route['spec']['host']]['http_ssl'] = False

    print(yaml.dump({args.hierakey: hieradata}, default_flow_style=False))


if __name__ == '__main__':
    main()
