# -*- coding: utf-8 -*-
# pebble - Passman client
# Copyright (C) 2018 Damien Goutte-Gattat
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

from . import command
from . import delete
from . import edit
from . import list
from . import new
from . import shell
from . import show


def get_command_list():
    cmdlist = command.CommandList()
    cmdlist.add(delete.DeleteCommand())
    cmdlist.add(edit.EditCommand())
    cmdlist.add(list.ListCommand())
    cmdlist.add(new.NewCommand())
    cmdlist.add(show.ShowCommand())
    cmdlist.add(shell.ShellCommand(cmdlist))

    return cmdlist
