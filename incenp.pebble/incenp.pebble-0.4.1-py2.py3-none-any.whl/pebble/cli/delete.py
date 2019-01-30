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

from .command import Command
from ..util import Error

try:
    input = raw_input
except NameError:
    pass


class DeleteCommand(Command):

    def __init__(self):
        super(DeleteCommand, self).__init__('del', "delete a credential",
             "delete credential with specified ID")

    def prepare_parser(self, parser):
        parser.add_argument('id', type=int,
                            help="credential ID to delete")

    def execute(self, vault, args):
        cred = vault.get(args.id)
        if not cred:
            raise Error("No credential found with ID {}".format(args.id))
        answer = input(u"Really delete credential '{}' (y/N)? ".format(cred['label']))
        if answer == 'y':
            vault.delete(cred)
