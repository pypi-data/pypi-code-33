# Copyright 2015-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections

from dewi_core.loader.context import Context
from dewi_core.loader.plugin import Plugin


class DewiPlugin(Plugin):
    def get_description(self) -> str:
        return "DEWI application plugin"

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi_commands.CommandsPlugin'}

    def load(self, c: Context):
        pass
