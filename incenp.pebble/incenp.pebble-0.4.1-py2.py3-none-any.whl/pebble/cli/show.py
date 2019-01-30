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

_fields = [
        ('description', 'Description', None),
        ('tags', 'Tags', lambda tags: ', '.join([tag[u'text'] for tag in tags])),
        ('url', 'URL', None),
        ('username', 'Username', None),
        ('email', 'Email', None),
        ('password', 'Password', None)
        ]

class ShowCommand(Command):

    def __init__(self):
        super(ShowCommand, self).__init__('show', "show credential(s)",
              "show credentials matching the given pattern(s); \
               if no pattern is given, show all credentials")

    def prepare_parser(self, parser):
        parser.add_argument('pattern', nargs='*',
                            help="the pattern(s) to search in the vault")
        parser.add_argument('-i', '--id', type=int, default=-1,
                            help="credential ID to show")

    def execute(self, vault, args):
        if args.id != -1:
            creds = [vault.get(args.id, decrypt=True)]
        else:
            creds = vault.search(args.pattern, decrypt=True)
        for cred in creds:
            self._print_credential(cred)

    def _print_credential(self, cred, out=sys.stdout):
        out.write(u"+---- {} ({}) -----\n".format(cred['label'],
                  cred['credential_id']))
        for field_name, field_label, field_format in _fields:
            if cred[field_name]:
                if field_format:
                    formatted_field = field_format(cred[field_name])
                else:
                    formatted_field = cred[field_name]
                out.write(u"| {}: {}\n".format(field_label, formatted_field))
        if cred['custom_fields']:
            for custom in cred['custom_fields']:
                out.write(u"| {}: {}\n".format(custom[u'label'],
                          custom[u'value']))
        out.write("+----\n")
