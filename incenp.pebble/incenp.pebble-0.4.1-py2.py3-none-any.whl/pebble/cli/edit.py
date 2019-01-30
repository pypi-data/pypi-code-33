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
from ..util import Error

class EditCommand(Command):

    def __init__(self):
        super(EditCommand, self).__init__('edit', "edit existing credential",
             "modify the credential with specified ID")

    def prepare_parser(self, parser):
        parser.add_argument('id', type=int,
                            help="credential ID to edit")
        parser.add_argument('--json', '-j', action='store_true',
                            help="edit credential as JSON")

    def execute(self, vault, args):
        cred = vault.get(args.id, decrypt=True)
        if not cred:
            raise Error("No credential found with ID {}".format(args.id))
        updated = edit_credential(cred, as_json=args.json)
        if updated:
            vault.update(updated)
        else:
            sys.stdout.write("No changes\n")
