# Copyright 2015-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections

from dewi_core.loader.context import Context
from dewi_core.loader.plugin import Plugin


class ImageHandlerCommandsPlugin(Plugin):
    def get_description(self):
        return "Commands to collect / sort / copy / delete images (photos)"

    def get_dependencies(self) -> collections.Iterable:
        return {
            'dewi_commands.commands.collect_images.ImageCollectorPlugin',
            'dewi_commands.commands.deduplicate_images.ImageDeduplicatorPlugin',
            'dewi_commands.commands.safe_delete_images.SafeEraserPlugin',
            'dewi_commands.commands.select_images.ImageSelectorPlugin',
            'dewi_commands.commands.sort_photos.PhotoSorterPlugin',
        }

    def load(self, c: Context):
        pass


class CommandsPlugin(Plugin):
    def get_description(self) -> str:
        return "Commnands of DEWI"

    def get_dependencies(self) -> collections.Iterable:
        return {
            'dewi_commands.commands.ImageHandlerCommandsPlugin',
            'dewi_commands.commands.edit.edit.EditPlugin',
            'dewi_commands.commands.filesync.FileSyncPlugin',
            'dewi_commands.commands.license.LicensePlugin',
            'dewi_commands.commands.lithurgical.LithurgicalPlugin',
            'dewi_commands.commands.split_zorp_log.SplitZorpLogPlugin',
            'dewi_commands.commands.ssh_ubuntu_windows.SshToUbuntuOnWindowsPlugin',
        }

    def load(self, c: Context):
        pass
