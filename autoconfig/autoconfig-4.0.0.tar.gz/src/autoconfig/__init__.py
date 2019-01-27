
__all__ = ['init', 'is_initialized']

import os, sys, inspect
from os.path import exists, isdir, abspath, join, dirname, isabs

try:
    import configparser
except ImportError:
    # Python 2
    import ConfigParser as configparser


_filename = None
# The fully qualified config file that was found by init.


def init(filename='.config', searchfrom=None, env='env', relpath=None, otherfiles=None):
    """
    filename
      The name of the configuration file.

      This can be a simple filename, in which case the file will be searched for.  It can also
      be a fully qualified filename such as '/etc/project.conf'.

      If not provided, a file named ".config" will be searched for.

    searchfrom
      Optional directory to start searching from.  If not provided, the default is the current
      working directory.  To search from the directory where the calling code is located, use::

        autoconfig.init(searchfrom=__file__)

      This parameter is ignored if `filename` is a path since no search is performed.

    env
      Optional section names whose contents are put into environment variables and can update
      the PYTHONPATH.

    relpath
      One or more directories (as a single string or a sequence of strings), relative to the
      caller (not the config file or current directory) to append to the system path.

      This is useful for scripts that have a private library directory, particularly in a
      mono-repo design with many small utilities.  If a library is specifically for a
      particular utility, it may be confusing to put it into a global area.

        autoconfig.init(relpath='lib')

    otherfiles
      Additional files that environment variables will be read from.  This can be a filename
      string or a list of filenames.  Like the main configuration file, these can be fully
      qualified or they will be searched for.

      These override values from the main configuration file and later filenames overwrite
      earlier ones.

    Raises FileNotFoundError if the configuration file is not found.
    """
    global _filename

    filenames = [_locate_config(filename, searchfrom)]

    if otherfiles:
        filenames.extend([_locate_config(other, searchfrom) for other in otherfiles])

    # A ConfigParser can read in multiple files, but if we are setting the python path it is
    # relative to the config file and each file does not have to be in the same directory.
    # Process them individually.

    for ix, fn in enumerate(filenames):
        p = Parser()
        p.read(fn)

        _copy_env(fn, p, env)

        if ix == 0:
            _add_relpath(relpath)
            _filename = fn

            _process_imports(p)


def is_initialized():
    """
    Return True if init has already been called; False otherwise.
    """
    return bool(_filename)


def get_filename():
    """
    Returns the fully qualified name of the config file found by init.
    """
    return _filename


class Parser(configparser.ConfigParser):
    # I want to use Python's ConfigParser to read the file, but it lowercases keys by default.
    # This is not acceptable for the [env] section.  I would like other sections to lowercase,
    # however, and there doesn't seem to be a good way to do that.  I tried providing a Boolean
    # and toggling it but that doesn't work.  For now I'm going to keep the case and lowercase
    # the keys myself.
    def __init__(self):
        kwargs = {}
        if sys.version_info[0] >= 3:
            kwargs['interpolation'] = configparser.ExtendedInterpolation()
            kwargs['comment_prefixes'] = '#'
        configparser.ConfigParser.__init__(self, allow_no_value=True, **kwargs)

    def optionxform(self, option):
        return option


def _is_str(value):
    """
    Returns True if value is a string or, in Python 2 a unicode object.
    """
    if sys.version_info[0] == 2:
        if isinstance(value, bytes):
            return True
    return isinstance(value, str)


def _copy_env(fqn, p, env):
    """
    Copies the items from the [env] section, and any additional sections listed in 'env'
    to os.environ.

    If PYTHONPATH is provided, it is parsed and prefixed to the system path.

    fqn
      The fully qualified path of the configuration file.

    p
      The ConfigParser

    env
      Optional list of environment sections to add to the environment.
    """
    if _is_str(env):
        env = [env]

    paths = []

    root = dirname(fqn)

    for name in env:
        if name in p.sections():
            for key in p.options(name):
                value = p.get(name, key)
                if value is None or value == '':
                    # A key with no value is used to "unset".
                    if key in os.environ:
                        del os.environ[key]
                else:
                    if key == 'PYTHONPATH':
                        a = _make_absolute(root, value)
                        if a:
                            value = os.pathsep.join(a)
                            paths.extend(a)

                    # Do we need to check the encoding?
                    os.environ[key] = value

    # If we found any PYTHONPATH entries, add them to the system path.  Make sure you keep the
    # original order.  If they are not fully qualified, they are relative to the configuration
    # file

    if paths:
        sys.path[:0] = paths


def _make_absolute(root, paths):
    """
    Given a string of one or more paths, split them into an array and make relative paths
    absolute.

    * root: The fully-qualified directory applied to relative directories in `paths`.
    * paths: A path string using the operating systems path separator ("/usr:/sys" or
      "c:\test;c:\bogus").
    """
    paths = [p.strip() for p in paths.strip().split(os.pathsep) if p.strip()]
    if not paths:
        return None
    return [(p if isabs(p) else join(root, p)) for p in paths]


def _locate_config(filename, searchfrom):
    """
    Locates the configuration file.

    We're going to allow filename to be a path to a different file so we can accept __file__.
    """
    if os.sep in filename and searchfrom:
        raise ValueError('Cannot provide a path in `filename` and a `searchfrom` value.')

    if isabs(filename):
        if not exists(filename):
            raise FileNotFoundError('Did not find configuration file.  filename=%r' % filename)
        return filename

    searchfrom = abspath(searchfrom or os.getcwd())
    path = searchfrom

    while 1:
        if isdir(path):
            fqn = join(path, filename)
            if exists(fqn) and not isdir(fqn):
                return fqn

        parent = dirname(path)
        if parent == path:
            raise FileNotFoundError('Did not find configuration file.  filename=%r searchfrom=%s' % (filename, searchfrom))
        path = parent


def _add_relpath(relpath):
    """
    If relpath was provided, add each entry in it to the Python path.
    """
    paths = _path_to_list(relpath)
    if not paths:
        return

    # Entries are relative to the *caller* of init.  We'll inspect the stack and backup.  (This
    # is what makes Python awesome.  Yes it is hard to optimize because of this, but when you
    # need it is great.)
    #
    # Frames:
    # * 0 - this function
    # * 1 - the init function that called this function
    # * 2 - the caller of init  <--  Hello, Sailor!

    frames = inspect.stack()
    if not frames:
        raise RuntimeError('Stack traces are not supported by this Python environment')
    root = dirname(frames[2][1])

    for path in paths:
        if not isabs(path):
            path = join(root, path)
        sys.path.append(path)


def _path_to_list(path):
    """
    Accepts a string or list of strings, each being a set of paths separated by the
    OS path separator (os.pathsep, e.g. ':' on Liux, ';' on Windows).
    """
    if path is None:
        return None

    if isinstance(path, str):
        paths = [path]

    result = []
    for p in paths:
        result.extend(part.strip() for part in p.split(os.pathsep))
    result = [part for part in result if part]
    return result


def _process_imports(parser):
    """
    Import the module or modules listed by the `module` key.
    """
    if not parser.has_option('import', 'module'):
        return
    value = parser.get('import', 'module')

    import importlib

    for modname in value.strip().split():
        importlib.import_module(modname)
