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
from .command import Command

class ListCommand(Command):

    def __init__(self):
        super(ListCommand, self).__init__('list', "list credentials",
             "list credentials matching the given pattern(s); \
              if no pattern is given, list all credentials")

    def prepare_parser(self, parser):
        parser.add_argument('pattern', nargs='*',
                            help="the pattern(s) to search in the vault")
        parser.add_argument('-i', '--id', action='store_true',
                            help="display credential ids")

    def execute(self, vault, args):
        creds = vault.search(args.pattern)
        for cred in creds:
            if args.id:
                sys.stdout.write(u"{}:{}\n".format(cred['credential_id'],
                                 cred['label']))
            else:
                sys.stdout.write(u"{}\n".format(cred['label']))
