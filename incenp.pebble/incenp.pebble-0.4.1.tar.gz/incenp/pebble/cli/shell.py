# -*- coding: utf-8 -*-
# pebble - Passman client
# Copyright (C) 2019 Damien Goutte-Gattat
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

import argparse
import readline
import sys

from .command import Command
from ..util import Error

try:
    input = raw_input
except NameError:
    pass


class ShellCommand(Command):

    def __init__(self, cmdlist):
        super(ShellCommand, self).__init__('shell', "start interactive shell")
        self.cmdlist = cmdlist
        self.loop = True

    def exit(self):
        self.loop = False

    def execute(self, vault, args):
        self.cmdlist.remove('shell')
        self.cmdlist.add(Command('exit', "exit the shell", callback=self.exit))
        self.cmdlist.add(Command('refresh', "refresh the cache",
            callback = lambda: vault.load(0)))

        parser = argparse.ArgumentParser(prog='pbl', add_help=False)
        self.cmdlist.prepare_parser(parser)

        readline.set_completer(CommandCompleter(self.cmdlist.names()).complete)
        readline.parse_and_bind('tab: complete')

        while self.loop:
            try:
                line = input("\npbl> ")
            except EOFError:
                sys.stdout.write("\n")
                break

            try:
                args = parser.parse_args(line.split())
            except SystemExit:
                continue

            try:
                self.cmdlist.execute(vault, args)
            except Error as e:
                sys.stdout.write(u"pbl: error: {}\n".format(e))


class CommandCompleter(object):
    # This class is heavily based on Doug Hellmann's example code on
    # <https://pymotw.com/2/readline/>, published under the BSD license.

    def __init__(self, commands):
        self.commands = sorted(commands)

    def complete(self, text, state):
        if state == 0:
            if text:
                self.matches = [s for s in self.commands if s.startswith(text)]
            else:
                self.matches = self.commands[:]

        try:
            response = self.matches[state]
        except IndexError:
            response = None

        return response
