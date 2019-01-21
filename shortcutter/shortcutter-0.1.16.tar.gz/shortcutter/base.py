import os
from os import path as p
from .exception import ShortcutError, ShortcutNoDesktopError, ShortcutNoMenuError
import re
import traceback


class ShortCutter(object):
    """
    Creates applicaton shortcuts for Windows, MacOS and Linux operating systems.

    To create desktop and menu shortcuts to ``python``::

        from shortcutter import ShortCutter
        s = ShortCutter()
        s.create_desktop_shortcut("python")
        s.create_menu_shortcut("python")

    Attributes:
    -----------
    raise_errors : bool=False
        Whether to raise exceptions or skip errors and continue.
    error_log : object=None
        File object where to write errors when ``raise_errors=False``.
        Default is None - do not write errors.
        Can also be ``sys.stderr`` or ``io.StringIO()``.
    desktop_folder : str
        Directory used when creating desktop shortcuts.
    menu_folder : str
        Directory used when creating menu shortcuts.
    bin_folder_pyexe : str
        ``Scripts`` or ``bin`` dir path. Simply closest to python executable path.
    bin_folder_shcut : str or None
        ``Scripts`` or ``bin`` dir path where shortcutter executable was installed.
    local_root : str
        Root directory path of the current python environment / installation.
        Derived from python executable path.
    activate : bool=True
        Whether to create shortcuts that automatically activate
        conda environment / virtual environment.
    exists : bool=True
        Whether the target should exist or not.
        If not then add ``/`` (``\\`` on Windows) at the end of the path to get dir shortcut.
    activate_args : tuple (str or None, str or None)
        First is the activate script full path (or None if it's wasn't found) - conda's or venv's.
        Second is the env argument of the activate script (or None if not needed).
    """

    def __init__(self, raise_errors=False, error_log=None, activate=True, exists=True):
        """
        Creates ShortCutter.

        Parameters
        ----------
        raise_errors : bool=False
            Whether to raise exceptions or skip errors and continue.
        error_log : object=None
            File object where to write errors when ``raise_errors=False``.
            Default is None - do not write errors.
            Can also be ``sys.stderr`` or ``io.StringIO()``.
        activate : bool=True
            Whether to create shortcuts that automatically activate
            conda environment / virtual environment.
        exists : bool=True
            Whether the target should exist or not.
            If not then add ``/`` (``\\`` on Windows) at the end of the path to get dir shortcut.
        """
        self._set_win_vars()  # important on Windows

        self.raise_errors = raise_errors
        self.error_log = error_log
        self.activate = activate
        self.exists = exists
        self.desktop_folder = self._get_desktop_folder()
        self.menu_folder = self._get_menu_folder()
        self.bin_folder_pyexe = self._get_bin_folder_pyexe()
        shortcutter = self.find_target('shortcutter')
        self.bin_folder_shcut = p.dirname(shortcutter) if shortcutter else self.bin_folder_pyexe
        self.local_root = self._get_local_root()
        self._ACTIVATE, self._ACTIVATE_PROMPT = self._get_activate_wrapper_templates()

        self.activate_args = self._get_activate_args()  # should be run the last

    # might be overridden if needed
    def _set_win_vars(self):
        pass

    # should be overridden
    @staticmethod
    def _get_desktop_folder():
        raise ShortcutError("_get_desktop_folder needs overriding")

    # should be overridden
    @staticmethod
    def _get_menu_folder():
        raise ShortcutError("_get_menu_folder needs overriding")

    # should be overridden
    @staticmethod
    def _get_bin_folder_pyexe():
        raise ShortcutError("_get_bin_folder_pyexe needs overriding")

    # should be overridden
    @staticmethod
    def _get_local_root():
        raise ShortcutError("_get_local_root needs overriding")

    # should be overridden
    @staticmethod
    def _get_activate_wrapper_templates():
        raise ShortcutError("_get_activate_wrapper_templates needs overriding")

    # should be overridden
    @staticmethod
    def _make_executable(file_path):
        raise ShortcutError("_make_executable needs overriding")

    def exe(self, app_name):
        """
        Returns platform independent executable name:

        * app > app (on Unix)
        * app > app.exe (on Windows)
        """
        if os.name == 'nt':
            return app_name + '.exe'
        else:
            return app_name

    def ba(self, script_name):
        """
        Returns platform independent shell script (bash/batch) name:

        * run > run (on Unix)
        * run > run.bat (on Windows)
        """
        if os.name == 'nt':
            return script_name + '.bat'
        else:
            return script_name

    def _get_activate_args(self):
        """
        Returns tuple: (str or None, str or None).

        First is the activate script full path (or None if it's wasn't found) - conda's or venv's.

        Second is the env argument of the activate script (or None if not needed).
        """
        if p.isdir(p.join(self.local_root, 'conda-meta')):
            # check if we are installing to conda root:
            activate = self._check_if_conda_root(self.local_root)
            if activate:
                return activate, None

            # check if we are installing to default conda env location:
            #   `<conda_root>/envs/<local_root_basename>`
            ddot = p.dirname(self.local_root)
            activate = self._check_if_conda_root(p.dirname(ddot))
            if (p.basename(ddot) == 'envs') and activate: 
                return activate, p.basename(self.local_root)

            # check if we are running pip via `conda env create -f env.yaml`
            #   or user specified `CONDA_ROOT` env var himself:
            conda_root = os.environ.get('CONDA_ROOT')
            activate = self._check_if_conda_root(conda_root)
            if activate:
                if p.isabs(conda_root):
                    return activate, self.local_root

            # check if there is conda in the PATH:
            conda = self.find_target('conda')
            if conda is not None:
                conda_root = p.dirname(p.dirname(conda))
                activate = self._check_if_conda_root(conda_root)
                if activate:
                    return activate, self.local_root

            return None, self.local_root
        else:
            # check if we are installing to venv:
            activate = p.join(self.bin_folder_pyexe, self.ba('activate'))
            if p.isfile(activate):
                return activate, None

        return None, None
 
    def _check_if_conda_root(self, path):
        """
        Checks if provided path is conda root. It should have
        conda-meta folder, conda executable, activate shell script.

        Returns path to conda activate script or None.
        """
        if path is not None:
            if p.isdir(p.join(path, 'conda-meta')):
                conda = p.join(path,
                               p.basename(self.bin_folder_pyexe),
                               self.exe('conda'))
                # check if the file executable:
                if p.isfile(conda) and os.access(conda, os.X_OK):
                    activate = p.join(p.dirname(conda), self.ba('activate'))
                    if p.isfile(activate):
                        return p.abspath(activate)
        return None

    def create_desktop_shortcut(self, target, shortcut_name=None):
        """
        Creates a desktop shortcut to a target.

        Parameters
        ----------
        target : str
            The target to create a shortcut for, it can be a fully qualified
            file path ``/path/to/my_program`` or a simple application name 
            ``my_program``.
        shortcut_name : str=None
            Name of the shortcut without extension (``.lnk`` would be appended if needed).
            If None uses the target filename.

        Returns
        -------
        tuple (str, str, str or None)
            (shortcut_name, target_path, shortcut_file_path)
        """
        if not p.isdir(self.desktop_folder):
            msg = "Desktop folder '{}' not found.".format(self.desktop_folder)
            if self.raise_errors:
                raise ShortcutNoDesktopError(msg)
            elif self.error_log is not None:
                self.error_log.write(msg + '\n')
        else:
            return self.create_shortcut(target, self.desktop_folder, shortcut_name)

    def create_menu_shortcut(self, target, shortcut_name=None):
        """
        Creates a menu shortcut to a target.

        Parameters
        ----------
        target : str
            The target to create a shortcut for, it can be a fully qualified
            file path ``/path/to/my_program`` or a simple application name 
            ``my_program``.
        shortcut_name : str=None
            Name of the shortcut without extension (``.lnk`` would be appended if needed).
            If None uses the target filename.

        Returns
        -------
        tuple (str, str, str or None)
            (shortcut_name, target_path, shortcut_file_path)
        """
        if not p.isdir(self.menu_folder):
            msg = "Menu folder '{}' not found.".format(self.menu_folder)
            if self.raise_errors:
                raise ShortcutNoMenuError(msg)
            elif self.error_log is not None:
                self.error_log.write(msg + '\n')
        else:
            return self.create_shortcut(target, self.menu_folder, shortcut_name)

    @classmethod
    def _path_to_name(cls, path):
        """
        Takes three last items from the absolutized path and converts to
        name by replacing everything except `A-Za-z0-9` to `_`
        """
        dirs = '_'.join(p.abspath(path).split(os.sep)[-3:-1])
        return cls._ascii_name('{}__at__{}'.format(p.basename(path), dirs))

    @staticmethod
    def _ascii_name(name):
        w_unicode_name = re.sub(r'\W', '_', name)
        w_ascii_name = str(w_unicode_name.encode('utf-8'))[1:].strip('"').strip("'").replace('\\', '_')
        return w_ascii_name

    def _create_wrapped_shortcut(self, shortcut_name, target_path, shortcut_directory, activate_args=None):
        """
        Creates shell script wrapper for shortcut with activation.
        
        Providing activate_args optional argument switches to creation
        of shortcut to terminal with activated environment.
        
        Returns a tuple of (shortcut_name, target_path, shortcut_file_path)
        """
        if activate_args is None:
            activate, env = self.activate_args
            terminals = False
            name = self._path_to_name(target_path)
        else:
            activate, env = activate_args
            terminals = True
            target_path = None
            name = self._ascii_name(shortcut_name)

        wrapper_path = p.join(self.bin_folder_shcut, self.ba('shortcutter__' + name))
        if target_path or terminals:
            def r(path):
                if path is None:
                    return ''
                else:
                    return path.replace('"', r'\"').replace("'", r"\'")

            def call_batch(path):
                if path is None:
                    return ''
                elif os.name == 'nt' and (path.endswith('.bat') or path.endswith('.cmd')):
                    return 'call '
                else:
                    return ''

            script = (self._ACTIVATE_PROMPT if terminals else self._ACTIVATE).format(
                activate=r(activate) + ('" "' + r(env) if env else ''),
                executable=r(target_path),
                bin=r(p.dirname(activate)),
                call=call_batch(target_path)
            )
            with open(wrapper_path, 'w') as f:
                f.write(script)
                self._make_executable(wrapper_path)
        return self._create_shortcut_file(shortcut_name, wrapper_path, shortcut_directory)

    def create_shortcut(self, target, shortcut_directory, shortcut_name=None):
        """
        Creates a shortcut to a target.

        Parameters
        ----------
        target : str
            The target to create a shortcut for, it can be a fully qualified
            file path ``/path/to/my_program`` or a simple application name 
            ``my_program``.
        shortcut_directory : str
            The directory path where the shortcut should be created.
        shortcut_name : str=None
            Name of the shortcut without extension (``.lnk`` would be appended if needed).
            If None uses the target filename.

        Returns
        -------
        tuple (str, str, str or None)
            (shortcut_name, target_path, shortcut_file_path)
        """
        # Set the target path:
        target_path = self.find_target(target)

        # Check if target is dir or file:
        isdir = False
        if target_path:
            if p.isdir(target_path):
                isdir = True

        if not target_path and not self.exists:
            if target.endswith(os.sep):
                isdir = True
            target_path = p.abspath(target)

        # Set shortcut name:
        if shortcut_name is None:
            if isdir:
                shortcut_name = p.basename(target)
            else:
                # getting the file name and removing the extension:
                shortcut_name = p.splitext(p.basename(target))[0]

        # Create shortcut function:
        def create():
            if not target_path:
                raise ShortcutError(
                    "Target '{}' wasn't found or invalid target/exists ('{}') options combination.".format(target,
                                                                                                           self.exists))

            if isdir:
                return self._create_shortcut_to_dir(shortcut_name, target_path, shortcut_directory)

            elif self.activate:
                activate, env = self.activate_args
                if activate:
                    return self._create_wrapped_shortcut(shortcut_name, target_path, shortcut_directory)

                elif (not activate) and env:
                    raise ShortcutError('Shortcutter failed to find conda root (or activate script there). ' +
                                        'It searched in `../../` assuming default env location ' +
                                        '(`../` should have `envs` basename). ' +
                                        'Checked `CONDA_ROOT` environment variable. ' +
                                        'Searched `conda` executable in the PATH.')
            # Use simple shortcuts if self.activate=False or we are installing to common python installation:
            return self._create_shortcut_file(shortcut_name, target_path, shortcut_directory)

        ret = self._safe_create(create)
        return ret if (ret != 'error') else (shortcut_name, target_path, None)

    def _safe_create(self, create):
        """
        Switches shortcuts creation function error modes.

        :param create:
            function to call (without arguments)
        """
        if self.raise_errors:
            ret = create()
        else:
            try:
                ret = create()
            except Exception:
                ret = 'error'
                if self.error_log is not None:
                    self.error_log.write(''.join(traceback.format_exc()))
        return ret

    def create_shortcut_to_env_terminal(self, shortcut_name=None, shortcut_directory=None, desktop=True, menu=True):
        """
        Creates shortcuts for console (terminal) that
        has already activated the environment we are installing to
        (plus shortcut to root environment in case of conda).

        Parameters
        ----------
        shortcut_name : str=None
            Name of the shortcut without extension (``.lnk`` would be appended if needed).
            If None uses the target filename.
        shortcut_directory : str=None
            The directory path where the shortcuts should be created.
        desktop : bool=True
            Whether to create shortcuts on the desktop.
        menu : bool=True
            Whether to create shortcuts in the menu.

        Returns
        -------
        bool
            True if all operations were successful, False otherwise.
        """
        activate, env = self.activate_args
        if not activate:
            return
        if not shortcut_name:
            shortcut_name = 'Terminal at '

        ret = []
        for check, path, pref in [(desktop, self.desktop_folder, 'Desktop folder'),
                                  (menu, self.menu_folder, 'Menu folder'),
                                  (shortcut_directory is not None, shortcut_directory, 'Directory')]:
            if check:
                if not p.isdir(path):
                    msg = "{} '{}' not found.".format(pref, path)
                    if self.raise_errors:
                        raise ShortcutNoDesktopError(msg)
                    elif self.error_log is not None:
                        self.error_log.write(msg + '\n')
                        ret.append('error')
                else:
                    name = shortcut_name + p.basename(p.dirname(p.dirname(activate)))
                    ret.append(self._safe_create(
                        lambda: self._create_wrapped_shortcut(name, None, path, (activate, None))
                    ))
                    if env:
                        name = shortcut_name + p.basename(env)
                        ret.append(self._safe_create(
                            lambda: self._create_wrapped_shortcut(name, None, path, (activate, env))
                        ))
        return False if ('error' in ret) else True

    # should be overridden
    def _create_shortcut_to_dir(self, shortcut_name, target_path, shortcut_directory):
        raise ShortcutError("_create_shortcut_to_dir needs overriding")

    # should be overridden
    def _create_shortcut_file(self, shortcut_name, target_path, shortcut_directory):
        raise ShortcutError("_create_shortcut_file needs overriding")

    def makedirs(self, *args):
        """
        Recursively creates dirs if they don't exist.
        Utilizes ``self.raise_errors`` and ``self.error_log``.
        
        Parameters
        ----------
        \*args : str
            Multiple paths (str) for folders to create.

        Returns
        -------
        bool
            True on success False of failure.
        """
        ret = []
        for path in args:
            if not p.isdir(path):
                ret.append(self._safe_create(lambda: os.makedirs(path)))

        return False if ('error' in ret) else True

    def find_target(self, target):
        """
        Finds a file path for a target application.
        Single-worded targets like ``'app'`` are always searched in the PATH.
        You should prepend ``./app`` to tell that the file is in the CWD.

        Parameters
        ----------
        target : str
            The target to find, it can be a fully qualified
            file path ``/path/to/my_program`` or a simple application name 
            ``my_program``.

        Returns
        -------
        str or None
            Returns a single target file path or ``None`` if a path can't be found.
        """
        if target:
            if p.basename(target) == target:
                targets = self.search_for_target(target)
                if len(targets) > 0:
                    return p.abspath(targets[0])
                else:
                    return None
            elif p.isfile(target) or p.isdir(target):
                return p.abspath(target)
        return None

    def search_for_target(self, target):
        """
        Searches for a target application.

        Parameters
        ----------
        target : str
            The target to find.

        Returns
        -------
        list(str)
            Returns a list of potential target file paths, it no paths are found an empty list is returned.
        """
        # potential list of app paths
        target_paths = []

        # create list of potential directories
        paths = self._get_paths()

        # loop through each folder
        for path in paths:
            if p.exists(path):
                if p.isdir(path):
                    # get files in directory
                    for file_name in os.listdir(path):
                        file_path = p.join(path, file_name)
                        if p.isfile(file_path):
                            if self._is_file_the_target(target, file_name, file_path):
                                target_paths.append(file_path)
                else:
                    # its not a directory, is it the app we are looking for?
                    pass

        return target_paths

    # needs overriding
    def _is_file_the_target(self, target, file_name, file_path):
        raise ShortcutError("_is_file_the_target needs overriding")

    # needs overriding
    @staticmethod
    def _get_paths():
        raise ShortcutError("_get_paths needs overriding")
