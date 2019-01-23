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

class Command(object):

    def __init__(self, name, help, description=None, callback=None):
        self._name = name
        self._help = help
        self._desc = description
        self._func = callback

    def prepare_parser(self, subparser):
        pass

    def execute(self, vault, args):
        if self._func:
            self._func()


class CommandList(object):

    def __init__(self):
        self._commands = {}

    def add(self, command):
        self._commands[command._name] = command

    def remove(self, name):
        self._commands.pop(name, None)

    def execute(self, vault, args):
        if args.command in self._commands:
            return self._commands[args.command].execute(vault, args)
        return False

    def prepare_parser(self, parser):
        subparsers = parser.add_subparsers(dest='command')
        for command in self._commands.values():
            subparser = subparsers.add_parser(command._name,
                    help=command._help, description=command._desc)
            command.prepare_parser(subparser)

    def names(self):
        return self._commands.keys()
