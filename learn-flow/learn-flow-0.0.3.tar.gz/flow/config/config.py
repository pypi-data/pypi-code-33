# -*- coding: utf-8 -*-
"""
Module config.py
----------------------
The main configuration module.
Defines the configuration class it loaders and parses.
"""
import os
import configparser
import yaml
import json
import types
import errno
import sys


# a marker that identifies that no value was passed to an optional named parameter
# this marker is used for named parameters that can the default value can not be None
_marker = object()


class ImportStringError(ImportError):
    """Provides information about a failed :func:`import_string` attempt."""

    #: String in dotted notation that failed to be imported.
    import_name = None
    #: Wrapped exception.
    exception = None

    def __init__(self, import_name, exception):
        self.import_name = import_name
        self.exception = exception

        msg = (
            'import_string() failed for %r. Possible reasons are:\n\n'
            '- missing __init__.py in a package;\n'
            '- package or module path not included in sys.path;\n'
            '- duplicated package or module name taking precedence in '
            'sys.path;\n'
            '- missing module, class, function or variable;\n\n'
            'Debugged import:\n\n%s\n\n'
            'Original exception:\n\n%s: %s')

        name = ''
        tracked = []
        for part in import_name.replace(':', '.').split('.'):
            name += (name and '.') + part
            imported = import_string(name, silent=True)
            if imported:
                tracked.append((name, getattr(imported, '__file__', None)))
            else:
                track = ['- %r found in %r.' % (n, i) for n, i in tracked]
                track.append('- %r not found.' % name)
                msg = msg % (import_name, '\n'.join(track),
                             exception.__class__.__name__, str(exception))
                break

        ImportError.__init__(self, msg)

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.import_name,
                                 self.exception)


def reraise(tp, value, tb=None):
    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)
    raise value


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    # __import__ is not able to handle unicode strings in the fromlist
    # if the module is a package
    import_name = str(import_name).replace(':', '.')
    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit('.', 1)
        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            module = import_string(module_name)

        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)

    except ImportError as e:
        if not silent:
            reraise(
                ImportStringError,
                ImportStringError(import_name, e),
                sys.exc_info()[2])


class Config(dict):
    """Works exactly like a dict but provides ways to fill it from files
    or special dictionaries.  There are two common patterns to populate the
    config.

    Either you can fill the config from a config file::

        app.config.from_pyfile('yourconfig.cfg')

    Or alternatively you can define the configuration options in the
    module that calls :meth:`from_object` or provide an import path to
    a module that should be loaded.  It is also possible to tell it to
    use the same module and with that provide the configuration values
    just before the call::

        DEBUG = True
        SECRET_KEY = 'development key'
        app.config.from_object(__name__)

    In both cases (loading from any Python file or loading from modules),
    only uppercase keys are added to the config.  This makes it possible to use
    lowercase values in the config file for temporary values that are not added
    to the config or to define the config keys in the same file that implements
    the application.

    Probably the most interesting way to load configurations is from an
    environment variable pointing to a file::

        app.config.from_envvar('YOURAPPLICATION_SETTINGS')

    In this case before launching the application you have to set this
    environment variable to the file you want to use.  On Linux and OS X
    use the export statement::

        export YOURAPPLICATION_SETTINGS='/path/to/config/file'
    """

    def __init__(self, defaults=None):
        dict.__init__(self, defaults or {})
        # the list of paths to search configuration
        # files ordered by its precedence
        self.search_paths = list()
        self.loaded_paths = set()

    def add_path(self, path: str):
        """
        Adds a config path to the last position of the search path list.
        :param path: a config file path string.
        """
        if path.startswith("~"):
            path = os.path.join(
                os.path.expanduser("~"),
                path[2:]
            )
        self.search_paths.append(path)

    def load_config(self):
        """Loads the configuration
        """
        try:
            for path in self.search_paths:
                # checks when the path has already been loaded
                if path not in self.loaded_paths:
                    if os.path.isfile(path):
                        filename, file_extension = os.path.splitext(path)
                        file_extension = file_extension.lower()
                        if file_extension in [".yml", ".yaml"]:
                            self.load_yaml_file(path)
                        elif file_extension in [".ini", ".conf", ".config", ".cfg"]:
                            self.load_ini_file(path)
                        elif file_extension == '.json':
                            self.load_json_file(path)
                        elif file_extension == '.py':
                            self.load_py_file(path)
                        else:
                            raise NotImplementedError(
                                "Configuration parser not implemented for the '{}' file extension. File path '{}'".format(
                                    file_extension, path
                                )
                            )
                    # add to the loaded paths
                    self.loaded_paths.add(path)
        except Exception as e:
            print("\nError: %s" % str(e), file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)

    def get_or_create_section(self, key):
        """
        Returns a configuration section.
        If it does not exists it will create a new section.
        :param key: the section name.
        :return: A Config object.
        """
        key = key.upper()
        if key in self:
            section = self[key]
        else:
            section = Config()
            section.search_paths = self.search_paths
            self[key] = section
        return section

    def load_ini_file(self, path):
        """Loads an .ini configuration file from the path received as parameter.
        This is basically just a shortcut for the config parser lib.

        The ini_file section name is concatenated with a dot ('.') plus the section config key.
        So the config name convention is: **'SECTION_NAME.CONFIG_KEY'**
        :Example: A configuration file named cong.ini
        .. code-block:: ini
            [DEFAULT]
            ServerAliveInterval = 45
            Compression = yes
        Then the the configuration will be loaded with the following keys:
            - 'DEFAULT.ServerAliveInterval'
            - 'DEFAULT.Compression'

        **Note**: it will never override n already existing config value.
        **Note**: You must not use dot '.' in yours config sections and keys it will break the lib
        since it uses dot as as simple way to walk through sections and structures

        :param path: a path string to the configuration file.
        :type path: str
        """
        # sanity check if the file exists
        if not os.path.isfile(path):
            return

        config = configparser.ConfigParser()
        config.read(path)
        # for each key/value
        # adds the key to the configuration object
        for section_name, section in config.items():
            # all values are upper cased
            section_name = section_name.upper()
            for key, value in section.items():
                # all keys are upper cased
                key = key.upper()
                # k is the section_name concatenated with '.' plus the config key
                if section_name in self:
                    self_section = self[section_name]
                else:
                    self_section = Config()
                    self_section.search_paths = self.search_paths
                    self[section_name] = self_section

                # it will never override an already existing config value
                if key not in self_section:
                    self_section[key] = value

    def load_yaml_file(self, path):
        """Loads an .yml/.yaml configuration file from the path received as parameter.
        This is basically just a shortcut for the pyYAML lib.

        The ini_file section name is concatenated with a dot ('.') plus the section config key.
        So the config name convention is: **'SECTION_NAME.CONFIG_KEY'**
        :Example: A configuration file named cong.ini
        .. code-block:: YAML
            build:
                context: ../../file-monitor
        Then the the configuration will be loaded with the following keys:
            - 'build.context'

        **Note**: it will never override n already existing config value.
        **Note**: You must not use dot '.' in yours config sections and keys it will break the lib
        since it uses dot as as simple way to walk through sections and structures

        :param path: a path string to the configuration file.
        :type path: str
        """
        # sanity check if the file exists
        if not os.path.isfile(path):
            return
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)
        # loads the parsed file
        self.load_dict(config)

    def load_dict(self, config):
        """
        loads the configuration from a dict parsed from the yaml file.
        :param config: a config dictionary parsed from the yaml file.
        """
        for key, value in config.items():
            key = key.upper()
            # when the value is a dict (section) object
            if isinstance(value, dict):
                section = self.get_or_create_section(key)
                # recursive call to load dict yaml function
                section.load_dict(value)

            elif isinstance(value, list):
                # it will never override a already loaded configuration
                if key in self:
                    continue
                else:
                    # TODO find a better solution
                    self[key] = list()
                for item in value:
                    self.load_list(self[key], item)
            # when the value is a string, int or float object
            else:
                # it will never override an already existing config value
                if key not in self:
                    self[key] = value

    def load_list(self, conf_list, values):
        """
        Loads the configuration list parsed from the yaml file.
        :param conf_list: the list used to store the configuration file.
        :param values: a list of values parsed from the yaml file.
        """
        for item in values:
            if isinstance(item, dict):
                section = Config()
                section.search_paths = self.search_paths
                section.load_dict(item)
                conf_list.append(section)
            elif isinstance(item, list):
                sub_list = list()
                conf_list.append(sub_list)
                self.load_list(sub_list, item)
            else:
                conf_list.append(item)

    def load_json_file(self, path):
        """Loads an .json configuration file from the path received as parameter.
        This is basically just a shortcut for the json lib.

        The json inner object is used as section in the configuration.
        The Section name is concatenated with a dot ('.') plus the section config key.
        So the config name convention is: **'SECTION_NAME.CONFIG_KEY'**
        :Example: A configuration file named conf.json
        .. code-block:: json
            ```{
                "section":{
                    "subsection":"value"
                }
            }```
        Then the the configuration will be loaded with the following keys:
            - 'section.subsection'

        **Note**: it will never override n already existing config value.
        **Note**: You must not use dot '.' in yours config sections and keys it will break the lib
        since it uses dot as as simple way to walk through sections and structures

        :param path: a path string to the configuration file.
        :type path: str
        """
        # sanity check if the file exists
        if not os.path.isfile(path):
            return

        with open(path, mode='r', encoding='utf-8') as f:
            json_str = f.read()
        conf = json.loads(json_str)
        self.load_dict(conf)

    def load_py_file(self, path):
        """Updates the values in the config from a Python file.  This function
        behaves as if the file was imported as module with the
        :meth:`from_object` function.

        :param path: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        """
        if not os.path.isfile(path):
            return

        d = types.ModuleType('config')
        d.__file__ = path
        try:
            with open(path, mode='rb') as config_file:
                exec(compile(config_file.read(), path, 'exec'), d.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)
        return True

    def from_object(self, obj):
        """Updates the values from the given object.  An object can be of one
        of the following two types:

        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly

        Objects are usually either modules or classes. :meth:`from_object`
        loads only the uppercase attributes of the module/class. A ``dict``
        object will not work with :meth:`from_object` because the keys of a
        ``dict`` are not attributes of the ``dict`` class.

        Example of module-based configuration::

            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)

        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.

        See :ref:`config-dev-prod` for an example of class-based configuration
        using :meth:`from_object`.

        :param obj: an import name or object
        """
        if isinstance(obj, str):
            obj = import_string(obj)

        for key in dir(obj):
            # it will never override an already loaded configuration
            if key.isupper() and key not in self:
                self[key.upper()] = getattr(obj, key)

    def get_section(self, section, lowercase=True):
        """**DEPRECATED**
        Returns a dictionary containing a subset of configuration options
        that match the specified namespace/prefix. Example usage::

            app.config['IMAGE_STORE_TYPE'] = 'fs'
            app.config['IMAGE_STORE_PATH'] = '/var/app/images'
            app.config['IMAGE_STORE_BASE_URL'] = 'http://img.website.com'
            image_store_config = app.config.get_namespace('IMAGE_STORE_')

        The resulting dictionary `image_store_config` would look like::

            {
                'type': 'fs',
                'path': '/var/app/images',
                'base_url': 'http://img.website.com'
            }

        This is often useful when configuration options map directly to
        keyword arguments in functions or class constructors.

        :param section: a configuration namespace
        :param lowercase: a flag indicating if the keys of the resulting
                          dictionary should be lowercase
        :return: A Config object representing the section.
        """
        rv = Config()
        sec = self.get(section, rv)
        for k, v in sec:
            if lowercase:
                rv[k.upper()] = v
            else:
                rv[k] = v
        return rv

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, dict.__repr__(self))

    def __getitem__(self, item):
        item = item.upper()
        value = self.get(item)
        if value is None and item not in self:
            raise KeyError(item)
        return value

    def __setitem__(self, key, value):
        self.set(key, value)

    def get(self, k, default=_marker):
        """
        Gets a value for the configuration with name k.
        :param k: a config key.
        :param default: a default value to be returned when the key is not found.
        :return: a value for the configuration.
        """
        k = k.upper()
        # environment variables will aways override any file loaded configuration
        env_conf = os.getenv(k, _marker)
        if env_conf is not _marker:
            return env_conf

        # split dotted path
        keys = k.split(".")
        conf = self
        # for each key in dotted path
        # we walk in the config dictionary
        for key in keys:
            # empty key is not allowed
            if key is "":
                continue
            conf = dict.get(conf, key, default)
            # conf was not found
            if conf is default or conf is None:
                break
        if conf is _marker:
            return None
        return conf

    def set(self, key, value):
        """
        Sets a key/value to the config.
        :param key: a config key.
        :param value: a configuration value.
        """
        key = key.upper()
        # environment variables will aways override any file loaded configuration
        env_conf = os.getenv(key, _marker)
        if env_conf is not _marker:
            env_val = os.environ.pop(key)

        # split dotted path
        keys = key.split(".")
        conf = self
        # for each key in dotted path
        # we walk in the config dictionary
        for key in keys[:-1]:
            # empty key is not allowed
            if key is "":
                continue

            conf = conf.get_or_create_section(key)
        dict.__setitem__(conf, keys[-1], value)
        # conf[key] = value
