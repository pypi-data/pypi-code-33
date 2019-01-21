import sys
import os
from os import path as p
import stat
from .base import ShortCutter

ACTIVATE = """#!/bin/bash
export PYTHONNOUSERSITE=1
source "{activate}"
"{executable}" "$@"
source "{bin}/deactivate"
"""

ACTIVATE_PROMPT = """#!/bin/bash
bash --rcfile <(echo 'export PATH="{bin}:$PATH"; export PYTHONNOUSERSITE=1; source "{activate}"; cd $HOME')
"""


class ShortCutterLinux(ShortCutter):
    @staticmethod
    def _get_desktop_folder():
        import subprocess
        try:
            return subprocess.check_output(['xdg-user-dir',
                                            'DESKTOP']).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return p.join(p.expanduser('~'), 'Desktop')

    @staticmethod
    def _get_menu_folder():
        return p.join(p.expanduser('~'), '.local', 'share', 'applications')

    @staticmethod
    def _get_bin_folder_pyexe():
        return p.dirname(sys.executable)

    @staticmethod
    def _get_local_root():
        return p.dirname(p.dirname(sys.executable))

    @staticmethod
    def _get_activate_wrapper_templates():
        return ACTIVATE, ACTIVATE_PROMPT

    @staticmethod
    def _make_executable(file_path):
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC)

    def _create_shortcut_to_dir(self, shortcut_name, target_path, shortcut_directory):
        """
        Creates a Linux shortcut file to executable.
        """
        return self._create_shortcut_linux(shortcut_name, target_path, shortcut_directory,
                                           '[Desktop Entry]\n' +
                                           'Name={}\n'.format(shortcut_name) +
                                           'Type=Application\n' +
                                           'Path={}\n'.format(target_path) +
                                           'Exec=xdg-open "{}"\n'.format(target_path) +
                                           'Icon=system-file-manager.png\n')

    def _create_shortcut_file(self, shortcut_name, target_path, shortcut_directory):
        """
        Creates a Linux shortcut file to folder.
        """
        return self._create_shortcut_linux(shortcut_name, target_path, shortcut_directory,
                                           '[Desktop Entry]\n' +
                                           'Name={}\n'.format(shortcut_name) +
                                           'Type=Application\n' +
                                           'Exec="{}" %F\n'.format(target_path) +
                                           'Terminal=true\n')

    def _create_shortcut_linux(self, shortcut_name, target_path, shortcut_directory, script):
        """
        Creates a Linux shortcut file using .desktop file script

        Returns tuple (shortcut_name, target_path, shortcut_file_path)
        """
        shortcut_file_path = p.join(shortcut_directory, shortcut_name + '.desktop')

        with open(shortcut_file_path, "w") as shortcut:
            shortcut.write(script)
            self._make_executable(shortcut_file_path)

        return shortcut_name, target_path, shortcut_file_path

    def _is_file_the_target(self, target, file_name, file_path):
        match = False
        if file_name == target:
            # is the file executable
            if os.access(file_path, os.X_OK):
                match = True
            else:
                match = False
        return match

    @staticmethod
    def _get_paths():
        """
        Gets paths from the PATH environment variable and
        prepends the `<Python>/bin` directory.

        Returns a list of paths.
        """
        return [p.dirname(sys.executable)] + os.environ['PATH'].split(os.pathsep) + [p.join(p.expanduser('~'), '.local', 'bin')]
