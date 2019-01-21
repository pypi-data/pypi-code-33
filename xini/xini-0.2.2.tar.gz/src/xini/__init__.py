"""
xini

Extract pyproject.toml configs to ini.

Usage:
  xini [--help] [--version]

Options:
  -h --help     Show this help message.
  -v --version  Show xini version.

"""
import sys
from pathlib import Path
import docopt
import toml

__version__ = "0.2.2"


class INIWriter:
    def __init__(self, toml_section_name, tool_inifile_name):
        self.toml_section_name = toml_section_name
        self.tool_inifile_name = tool_inifile_name
        self.filepath = Path.cwd() / self.tool_inifile_name
        self._output = []

    def _write(self, content):
        self._output.append(content)

    def get_section_from_toml(self, toml_cfg):
        #  print(toml_cfg)
        print(f"Searching for `{self.toml_section_name}` section...")
        section = toml_cfg
        for name in self.toml_section_name.split("."):
            section = section.get(name)
            if not section:
                print(f"    [{self.toml_section_name}] does not exist.")
                break
        return name, section  # pylint: disable=undefined-loop-variable

    def write_section(self, name):
        self._write(f"[{name}]")

    def _convert(self, key, value):
        # pylint: disable=no-else-return
        if isinstance(value, str):
            return value
        elif isinstance(value, bool):
            return "true" if value is True else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            slst = [self._convert(key, val) for val in value]
            if len(slst) <= 5:
                return ",".join(slst)
            # if there's more than 5 items in the list, place them
            # on separate lines, and left-align with the placement
            # the first value after the `key = `.
            joiner = f",\n" + (" " * (len(key) + 3))
            return joiner.join(slst)
        return

    def write_keyvalue(self, key, value):
        _v = self._convert(key, value)
        self._write(f"{key} = {_v}")

    def write_ini(self, section_name, toml_cfg):
        if not toml_cfg:
            return
        self.write_section(section_name)
        for k, v in toml_cfg.items():
            if isinstance(v, dict):
                self.write_ini(k, v)
            else:
                self.write_keyvalue(k, v)

    def extract_config(self, toml_cfg):
        section_name, section_cfg = self.get_section_from_toml(toml_cfg)
        if section_cfg:
            print(f"    Extracting {self.tool_inifile_name}.")
            self.write_ini(section_name, section_cfg)

    def __str__(self):
        return "\n".join(self._output)

    def save(self):
        with self.filepath.open(mode="w") as _fh:
            _fh.write(str(self))
        print(f"    Saved to: {self.tool_inifile_name}.")


INI_FILES = {
    "flake8": INIWriter("tool.flake8", ".flake8"),
    "pytest": INIWriter("tool.pytest", "pytest.ini"),
    "coverage": INIWriter("tool.coverage", ".coveragerc"),
    "pylint": INIWriter("tool.pylint", ".pylintrc"),
}


def load_toml(path_string="pyproject.toml"):
    pyproject = Path(path_string)

    if not pyproject.exists():
        print("Could not find pyproject.toml file.")
        sys.exit(1)

    return toml.load(pyproject)


def toml_2_ini():

    toml_cfg = load_toml()

    for ini_cfg in INI_FILES.values():
        ini_cfg.extract_config(toml_cfg)
        ini_cfg.save()


def main():
    docopt.docopt(__doc__, version=__version__)
    toml_2_ini()
