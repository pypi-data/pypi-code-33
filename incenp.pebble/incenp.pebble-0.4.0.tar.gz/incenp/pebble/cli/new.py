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
from ..editor import edit_credential

class NewCommand(Command):

    def __init__(self):
        super(NewCommand, self).__init__('new', "create a new credential",
             "add a new credential to the store")

    def prepare_parser(self, parser):
        parser.add_argument('--json', '-j', action='store_true',
                            help="edit new credential as JSON")

    def execute(self, vault, args):
        template = {
                'label': '',
                'description': '',
                'created': None,
                'changed': None,
                'tags': [],
                'email': '',
                'username': '',
                'password': '',
                'url': '',
                'favicon': '',
                'renew_interval': 0,
                'expire_time': 0,
                'delete_time': 0,
                'files': [],
                'custom_fields': [],
                'otp': {},
                'hidden': False
                }
        newcred = edit_credential(template, as_json=args.json)
        if newcred:
            if vault.test_decryption():
                vault.add(newcred)
        else:
            sys.stdout.write("No changes\n")
