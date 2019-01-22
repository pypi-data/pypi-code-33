# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections

from dewi_core.loader.context import Context
from dewi_core.loader.plugin import Plugin


class CommandsPlugin(Plugin):
    def get_description(self) -> str:
        return "Commands of DEWI"

    def get_dependencies(self) -> collections.Iterable:
        return {
            'dewi_commands.commands.CommandsPlugin',
        }

    def load(self, c: Context):
        pass
