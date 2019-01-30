#!/usr/bin/env python

from pathlib import Path
import distutils
import os

def env_is_debug():
    try:
        truth = distutils.util.strtobool(os.getenv("DEBUG"))
    except ValueError:
        return False
    except AttributeError:
        return False

    return truth

def config_file():
    '''Return a path to the configuration file.
    '''

    for i in [ "./certs.yaml",
               "/".join([str(Path.home()), ".check_certs/certs.yaml"]),
             ]:
        if Path(i).is_file():
            return i
    else:
        return "/etc/check_certs/certs.yaml"

def deep_merge(a, b, level=0):
    '''Recursively merge 2 dicts a and b, go as deep as 9 levels.
    '''

    if level >= 9:
        return b
    else:
        level += 1

    # If neither a nor b is dict, no need to check further.
    if not isinstance(a, dict): return b
    if not isinstance(b, dict): return b

    for key in b:
        if key in a :
            a[key] = deep_merge(a[key], b[key])
        else:
            a[key] = b[key]

    return a

import argparse
def get_args(args=[]):
    parser = argparse.ArgumentParser(
        description='''Check TLS certificates of sites for their expiration
                    dates. Send notifications if configured to do so.'''
    )

    parser.add_argument(
        "-n", "--notify-when-expiring-in",
        default=35,
        type=int,
        help="notify when a certificate expires in this many days",
    )

    parser.add_argument(
        "-p", "--port",
        default=443,
        type=int,
        help="port number",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="just show certificate info, no notification sent",
    )

    parser.add_argument(
        "sites",
        nargs="*",
        help="a space-separated list of sites in either <fqdn> or <fqdn:port> format",
    )

    return parser.parse_args(args)
