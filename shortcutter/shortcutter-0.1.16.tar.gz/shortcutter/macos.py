from os import path as p
from .exception import ShortcutError
from .linux import ShortCutterLinux
from tempfile import NamedTemporaryFile
import subprocess


def create_shortcut(shortcut_name, target_path, shortcut_directory, script):
    """
    Creates a MacOS app which opens an target_path (executable or folder) using AppleScript script

    Returns tuple (shortcut_name, target_path, shortcut_file_path)
    """
    shortcut_file_path = p.join(shortcut_directory, shortcut_name + ".app")

    # create the AppleScript script
    sf = NamedTemporaryFile(mode="w")
    sf.write(script)
    sf.flush()

    # compile the script into an application
    result = subprocess.run(["osacompile", "-o", shortcut_file_path, sf.name], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if len(result.stderr):
        raise ShortcutError("Error occured creating app - {}".format(str(result.stderr)))

    sf.close()

    return shortcut_name, target_path, shortcut_file_path


class ShortCutterMacOS(ShortCutterLinux):
    @staticmethod
    def _get_desktop_folder():
        return p.join(p.expanduser('~'), 'Desktop')

    @staticmethod
    def _get_menu_folder():
        return p.join('/', 'Applications') 

    def _create_shortcut_to_dir(self, shortcut_name, target_path, shortcut_directory):
        """
        Creates a MacOS app which opens a folder via finder
        """
        return create_shortcut(shortcut_name, target_path, shortcut_directory,
                               'tell application "Finder"\n' +
                               'open POSIX file "{}"\n'.format(target_path) +
                               'end tell\n')

    def _create_shortcut_file(self, shortcut_name, target_path, shortcut_directory):
        """
        Creates a MacOS app which opens an executable via the terminal
        """
        return create_shortcut(shortcut_name, target_path, shortcut_directory,
                               'tell application "Terminal"\n' +
                               'activate\n' +
                               'do script "{}"\n'.format(target_path) +
                               'end tell\n')
