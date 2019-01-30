# -*- coding: utf-8 -*-
# pebble - Passman client
# Copyright (C) 2018,2019 Damien Goutte-Gattat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import argparse
from incenp.pebble import __version__
from incenp.pebble.server import Server
from incenp.pebble.cache import Vault
from incenp.pebble.cli import get_command_list
from incenp.pebble.util import Error, SecretCache

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser


prog_name = "pbl"
prog_notice = """\
{} (Pebble {})
Copyright © 2018,2019 Damien Goutte-Gattat

This program is released under the GNU General Public License.
See the COPYING file or <http://www.gnu.org/licenses/gpl.html>.
""".format(prog_name, __version__)


def die(msg):
    sys.stderr.write("{}: {}\n".format(prog_name, msg))
    sys.exit(1)


class VersionAction(argparse.Action):

    def __init__(self, option_strings, dest):
        super(VersionAction, self).__init__(option_strings, dest,nargs=0,
                help="show information about the program and exit")

    def __call__(self, parser, namespace, values, option_string=None):
        parser.exit(prog_notice)


def get_server_options(config, section):
    if config.has_option(section, 'server'):
        server_section_name = config.get(section, 'server')
        if not config.has_section(server_section_name):
            die("No server section '{}' in configuration file".format(
                server_section_name))
        else:
            return get_server_options(config, server_section_name)
    else:
        host = config.get(section, 'host')
        user = config.get(section, 'user')
        if config.has_option(section, 'password'):
            password = config.get(section, 'password')
        else:
            sc = SecretCache("Passphrase for {} on {}: ".format(user, host),
                             command=config.get(section, 'password_command',
                                                fallback=None))
            password = sc.get_secret

        return (host, user, password)


def parse_duration(s):
    n = s
    factor = 1
    if len(s) > 1 and s[-1] in ('m', 'h', 'd'):
        n = s[:-1]
        if s[-1] == 'm':
            factor = 60
        elif s[-1] == 'h':
            factor = 3600
        else:
            factor = 86400

    try:
        return int(n) * factor
    except ValueError:
        die("Improper duration value: {}".format(s))


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]

    home_dir = os.getenv('HOME', default='')
    conf_dir = '{}/pebble'.format(
            os.getenv('XDG_CONFIG_HOME',
                default='{}/.config'.format(home_dir)))
    data_dir = '{}/pebble'.format(
            os.getenv('XDG_DATA_HOME',
                default='{}/.local/share'.format(home_dir)))

    parser = argparse.ArgumentParser(prog=prog_name,
            description="Command-line client for Nextcloud's Passman.",
            epilog="Report bugs to <devel@incenp.org>.")
    parser.add_argument('-v', '--version', action=VersionAction)
    parser.add_argument('-c', '--config',
            default='{}/config'.format(conf_dir),
            help="path to an alternative configuration file")
    parser.add_argument('-s', '--section', default='default',
            help="name of configuration file section to use")
    parser.add_argument('-f', '--refresh', dest='refresh', action='store_true',
            help="always refresh the local cache")
    parser.add_argument('--no-refresh', dest='age', const=-1, action='store_const',
            help="do not refresh the local cache even if it is old")

    commands = get_command_list()
    commands.prepare_parser(parser)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_usage()
        parser.exit()

    config = ConfigParser()
    config.read(args.config)

    if not config.has_section(args.section):
        die("No section '{}' in configuration file".format(args.section))

    vault_name = config.get(args.section, 'vault')
    server = Server(*get_server_options(config, args.section))
    sc = SecretCache("Passphrase for vault {} on {}@{}: ".format(vault_name,
                     server.user, server.host))
    caching = not(config.getboolean(args.section, 'nocache', fallback=False))
    vault = Vault(server, vault_name, data_dir, sc.get_secret, caching=caching)

    if args.refresh:
        max_age = 0
    else:
        max_age_str = config.get(args.section, 'max_age', fallback='86400')
        max_age = parse_duration(max_age_str)

    try:
        vault.load(age=max_age)
        commands.execute(vault, args)
    except Error as e:
        die(e)
    except KeyboardInterrupt:
        die("Interrupted")
    finally:
        server.close()


if __name__ == '__main__':
    main()
