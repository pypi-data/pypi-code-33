import os
import re
import sys
import inspect
import logging

import yaml
import json
import appdirs
import pkg_resources
from collections import OrderedDict

from .meta import TypeStructure
# from .containers import Structure, Dict, List
from . import containers, fields

FORMAT_YAML = ".yaml"
FORMAT_PYTHON = ".py"
FORMAT_JSON = ".json"


class ConfigFile(object):
    def __init__(self, config_path, config, appname=None, init=True):
        """
        Config file container.
        :param str config_path: path to file for storage. Either absolute
                                 or relative. If relative, appname is required
                                 to determine user config folder for platform
        :param Structure config: top level config item
        :param str appname: When using relative path fon config_file,
                             appname is required for user config dir
        """
        self.write_enabled = False
        self.config_path = str(config_path)
        # convert passed in config to a registered instance
        self.config = self.register_structure(config)
        conftype = config if config.__class__ is TypeStructure else config.__class__
        assert isinstance(self.config, conftype)
        self.log = logging.getLogger("Config")

        if not os.path.isabs(self.config_path):
            if not appname:
                try:
                    mainpkg = __import__('__main__').__package__.split('.')[0]
                    appname = pkg_resources.get_distribution(mainpkg).project_name
                except (AttributeError, IndexError):
                    raise ValueError("Must provide appname for relative config file path")
            appdir = appdirs.user_data_dir(appname=appname)
            if not os.path.exists(appdir):
                try:
                    os.makedirs(appdir)
                except:
                    pass
            self.config_path = os.path.join(appdir, self.config_path)

        # Startup
        if os.path.exists(self.config_path):
            config_name = self.config.__class__.__name__
            try:
                saved_config = self.load_config_file(self.config_path, config_name)
                if isinstance(saved_config, containers.Structure):
                    saved_config = saved_config.__getstate__()
                self.config.__setstate__(saved_config)
                self.config = self.register_structure(self.config)
                self.log.info("Loaded config from %s" % self.config_path)
            except IndexError:
                raise ValueError("class {config_name} not found in {path}".format(
                    config_name=config_name, path=self.config_path
                ))
            except ValueError:
                self.log.exception("Failed to load config from %s" % self.config_path)
        if init:
            self.init()

    @staticmethod
    def load_config_file(config_path, config_name=None):
        saved_config = None
        with open(config_path, 'r') as configfile:
            if config_path.endswith(FORMAT_PYTHON):
                config = configfile.read()
                locals = OrderedDict()
                globals = dict(**containers.__registered__)

                def mock_imports(match):
                    mocks = []
                    for mod in match.group(1).split(','):
                        mocks.append("{mod} = type('{mod}',(dict,),{{}})".format(mod=mod.strip()))
                    return '\n'.join(mocks)

                config = re.sub('(?:^|\n)import (.*)\n', mock_imports, config)

                exec(config, globals, locals)

                saved_config = [c for c in locals.values()
                                if config_name is None or
                                getattr(c, '__name__', '') == config_name][0]

            elif config_path.endswith(FORMAT_JSON):
                saved_config = json.load(configfile)
            else:
                try:
                    saved_config = yaml.load(configfile)
                except (TypeError, ValueError) as ex:
                    raise ValueError(str(ex))

        return saved_config

    def init(self):
        self.write_enabled = True

        # Ensure the config file exists for new installations.
        if not os.path.exists(self.config_path):
            self.write_yaml()
            self.log.info("Initialised new config file at %s" % self.config_path)

    def write_yaml(self):
        if self.write_enabled:
            try:
                os.makedirs(os.path.dirname(self.config_path))
            except OSError:
                pass
            with open(self.config_path, 'w') as configfile:
                if self.config_path.endswith(FORMAT_PYTHON):
                    with self.config.__raw_fields__():
                        self.write_python(self.config, configfile)
                elif self.config_path.endswith(FORMAT_JSON):
                    with self.config.__raw_fields__():
                        self.write_json(self.config, configfile)
                else:
                    yaml.dump(self.config, configfile,
                              default_flow_style=False, Dumper=NoAliasDumper)

    @staticmethod
    def write_json(config, configfile):
        json.dump(config, configfile, cls=StructureJsonEncoder, indent=4)

    @staticmethod
    def write_python(config, configfile):
        if not config:
            return
        name = config.__class__.__name__

        pg = PythonGenerator()

        pg.write("class {name}(Structure):".format(**locals())).indent()

        supports = set()

        def parse(_pg, key, val, in_list=False):

            if isinstance(val, fields.TypedField):
                if val.store_converted:
                    val = val.writer(val.value)
                else:
                    val = val.value

            elif isinstance(val, fields.Field):
                val = val.value

            if isinstance(val, (containers.List, list, tuple)):
                list_type = None
                content_types = {type(o) for o in val}
                if len(content_types) == 1:
                    list_type = content_types.pop()

                header = "List(" if list_type else "["
                footer = "type={})".format(list_type.__name__) if list_type else "]"

                if key:
                    _pg.write("{key} = {header}".format(**locals())).indent()
                else:
                    _pg.write(header).indent()
                [parse(_pg, None, v, in_list=True) for v in val]
                if key and not in_list:
                    _pg.dedent().write(footer)
                else:
                    _pg.dedent().write(footer+",")

            elif isinstance(val, (containers.Dict, dict)):
                if key:
                    _pg.write("{key} = dict(".format(**locals())).indent()
                else:
                    _pg.write("dict(").indent()

                [parse(_pg, k, v, in_list=True) for k, v in val.items()]

                if key:
                    _pg.dedent().write(")")
                else:
                    _pg.dedent().write("),")

            elif isinstance(val, containers.Structure):
                _name = val.__class__.__name__
                if key == _name:
                    key = None
                header = ""
                if key:
                    header = "%s = " % key

                if in_list or key:
                    supports.add(_name)
                    pg.write("{header}{_name}(".format(**locals())).indent()
                else:
                    pg.write("class {_name}(Structure):".format(**locals())).indent()

                for _key, _value in val:
                    parse(_pg, _key, _value, in_list=(in_list or key))

                pg.dedent()
                if in_list:
                    pg.write("),")
                elif key:
                    pg.write(")")

            elif in_list:
                rval = repr(val)
                if rval.startswith('<') and rval.endswith('>'):
                    raise ValueError("Don't know how to export %s to python" % val)
                if key is None:
                    _pg.write("{rval},".format(**locals()))
                else:
                    _pg.write("{key} = {rval},".format(**locals()))
            else:
                val = val.value if isinstance(val, fields.Field) else val
                rval = repr(val)
                _pg.write("{key} = {rval}".format(**locals()))

        for key, value in config:
            parse(pg, key, value)

        pydata = pg.end()

        if supports:
            pydata = "import " + ", ".join(sorted(supports)) + "\n\n" + pydata

        print(pydata)
        configfile.write(pydata)

    def register_structure(self, structure):
        """
        This will attach this config files' writer to the structure
        :param Structure structure: key to register
        :returns: structure as passed in
        """

        def attach(_structure):
            if inspect.isclass(_structure) and issubclass(_structure, containers.Structure):
                _structure = _structure()
            if isinstance(_structure, (containers.Structure, containers.List)):
                _structure.__reg_configfile__(self)
                attach_attrs(_structure)

            return _structure

        def register_val(_val):
            if isinstance(_val, dict):
                if not isinstance(_val, containers.Dict):
                    _val = containers.Dict(_val)

                for k, v in _val.items():
                    _val[k] = attach(v)
                _val.__reg_configfile__(self)

            elif isinstance(_val, (list, set, tuple)):
                list_type = None
                if isinstance(_val, containers.List):
                    list_type = _val.type
                _val = containers.List(*(attach(v) for v in _val), type=list_type)
            _val = attach(_val)
            return _val

        def attach_attrs(_structure):
            if isinstance(_structure, containers.Structure):
                for key, val in _structure:
                    val = register_val(val)
                    _structure[key] = val
                    if isinstance(val, fields.Deprecated):
                        continue

        structure = register_val(structure)

        attach_attrs(structure)

        return structure


def list_rep(dumper, data):
    """
    Ensure pyyaml treats our list as a regular list
    """
    return dumper.represent_list(list(data))


def dict_rep(dumper, data):
    """
    Ensure pyyaml treats our list as a regular list
    """
    return dumper.represent_dict(dict(data))


class NoAliasDumper(yaml.dumper.Dumper):
    """
    Disable alias when writing yaml as these make it harder to
    manually read/modify the config file
    """

    def ignore_aliases(self, data):
        return True


containers.__registered__["Structure"] = containers.Structure
containers.__registered__["List"] = containers.List

yaml.add_representer(containers.List, list_rep)

yaml.add_representer(containers.Dict, dict_rep)


class StructureJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, containers.Structure):
            return o.__as_dict__()

        elif isinstance(o, fields.TypedField):
            if o.store_converted:
                return o.writer(o.value)
            else:
                return o.value

        elif isinstance(o, fields.Field):
            return o.value


class PythonGenerator:

    def __init__(self, tab=" "*4):
        self.code = []
        self.tab = tab
        self.level = 0

    def end(self):
        return "\n".join(self.code)

    def write(self, string):
        self.code.append(self.tab * self.level + string)
        return self

    def indent(self):
        self.level = self.level + 1
        return self

    def dedent(self):
        if self.level == 0:
            raise SyntaxError("internal error in code generator")
        self.level = self.level - 1
        return self
