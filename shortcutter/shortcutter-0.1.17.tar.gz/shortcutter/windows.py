import sys
import site
import os
from os import path as p

# import win32com
# this often fails due to unable to find DLLs
# so dynamically change the path if required
try:
    import win32com
except ImportError as e:
    if "DLL load failed:" in str(e):
        path = p.join(p.split(sys.executable)[0], "Lib", "site-packages", "pywin32_system32")
        os.environ["PATH"] = os.environ["PATH"] + ";" + path
        try:
            import win32com
        except ImportError as ee:
            dll = os.listdir(path)
            dll = [p.join(path, _) for _ in dll if "dll" in _]
            raise ImportError("{}\n Failed to import win32com, due to missing DLL:\n".format(ee) + "\n".join(dll))
    else:
        raise e

from win32com.client import Dispatch
from .base import ShortCutter

shell = Dispatch('WScript.Shell')

ACTIVATE = r"""@echo off
set PYTHONNOUSERSITE=1
call "{activate}"
{call}"{executable}" %*
call "{bin}\deactivate.bat"
"""

ACTIVATE_PROMPT = """@echo off
set "PATH={bin};%PATH%"
set PYTHONNOUSERSITE=1
call "{activate}"
set "u=chcp 65001 && set PYTHONIOENCODING=utf-8"
set "a=chcp 1252 && set PYTHONIOENCODING="
set "b=set LANG=C.UTF-8 && set PYTHONIOENCODING=utf-8 && "%PROGRAMFILES%\Git\git-bash.exe""
cd /d %USERPROFILE%
cmd /k
"""

FOLDER_SHORTCUT = r"""@echo off
if exist "{path}\" (
    cd /d "{path}"
    start .
) else (
    echo Folder doesn't exist: "{path}"
    pause
)
"""


class ShortCutterWindows(ShortCutter):
    def _set_win_vars(self):
        self._executable_file_extensions = [ext.upper() for ext in os.environ['PATHEXT'].split(os.pathsep)]

    @staticmethod
    def _get_desktop_folder():
        return shell.SpecialFolders("Desktop")

    @staticmethod
    def _get_menu_folder():
        return shell.SpecialFolders("Programs")

    @staticmethod
    def _get_bin_folder_pyexe():
        return p.join(p.dirname(sys.executable), "Scripts")

    @staticmethod
    def _get_local_root():
        return p.dirname(sys.executable)

    @staticmethod
    def _get_activate_wrapper_templates():
        return ACTIVATE, ACTIVATE_PROMPT

    @staticmethod
    def _make_executable(file_path):
        pass

    def _create_shortcut_to_dir(self, shortcut_name, target_path, shortcut_directory):
        return self._create_shortcut_win(shortcut_name, target_path, shortcut_directory, True)

    def _create_shortcut_file(self, shortcut_name, target_path, shortcut_directory):
        return self._create_shortcut_win(shortcut_name, target_path, shortcut_directory)

    def _create_shortcut_win(self, shortcut_name, target_path, shortcut_directory, folder=False):
        """
        Creates a Windows shortcut file.

        Returns tuple (shortcut_name, target_path, shortcut_file_path)
        """
        icon = None
        if not folder:
            shortcut_target_path = target_path
            working_directory = p.dirname(target_path)
            ext = p.splitext(target_path)[1].upper()
            if ext in self._executable_file_extensions:
                icon = r'%SystemRoot%\System32\imageres.dll,11'

        elif not p.isdir(target_path):
            # create a bat script that opens the folder:
            
            wrapper_path = p.join(self.bin_folder_shcut, self.ba('shortcutter__dir__' + self._path_to_name(target_path)))
            with open(wrapper_path, 'w') as f:
                f.write(FOLDER_SHORTCUT.format(path=target_path))
            shortcut_target_path = wrapper_path
            working_directory = self.bin_folder_shcut
            icon = r'%SystemRoot%\explorer.exe,0'

        else:
            shortcut_target_path = target_path
            working_directory = target_path

        shortcut_file_path = p.join(shortcut_directory, shortcut_name + ".lnk")
        shortcut = shell.CreateShortCut(shortcut_file_path)
        shortcut.Targetpath = shortcut_target_path
        shortcut.WorkingDirectory = working_directory
        shortcut.Description = "Shortcut to" + p.basename(target_path)
        if icon:
            shortcut.IconLocation = icon
        shortcut.save()

        return shortcut_name, target_path, shortcut_file_path

    def _is_file_the_target(self, target, file_name, file_path):
        match = False
        # does the target have an extension?
        target_ext = p.splitext(target)[1]
        # if so, do a direct match
        if target_ext:
            if file_name.lower() == target.lower():
                match = True
        # no extension, compare the target to the file_name for each executable file extension
        else:
            for extension in self._executable_file_extensions:
                if file_name.lower() == (target + extension).lower():
                    match = True
        return match

    @staticmethod
    def _get_paths():
        """
        Gets paths from the PATH environment variable and 
        prepends `<Python>`, `<Python>\Scripts`, `<Python>\Library\bin` directories.

        Returns a list of paths.
        """
        root = p.dirname(sys.executable)
        user_root = p.dirname(site.USER_SITE)
        return [root,
                p.join(root, 'Scripts'),
                p.join(root, 'Library', 'bin')
               ] + os.environ['PATH'].split(os.pathsep) + [p.join(user_root, 'Scripts')]
