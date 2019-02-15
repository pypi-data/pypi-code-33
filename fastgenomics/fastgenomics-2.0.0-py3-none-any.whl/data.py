from pathlib import Path
from collections import OrderedDict
import json

from .defaults import DEFAULT_DATA_ROOT

DATA_SUBDIRS = ["data", "config", "output", "summary"]


class FGData(object):
    """This class stores the paths to data structured according to the
fastgenomics specification.  It also loads the input file mappings and
checks if the files exist.

    """

    _subdirs = DATA_SUBDIRS
    _mandatory_files = ["config/input_file_mapping.json"] + DATA_SUBDIRS

    def __init__(self, data_root=DEFAULT_DATA_ROOT):
        if isinstance(data_root, str):
            data_root = Path(data_root)
        self.root = data_root
        self.check_files()

        self.paths = self.get_paths()
        self.input_file_mapping = self.get_input_file_mapping()
        self.parameters = self.get_parameters()

    def get_input_file_mapping(self):
        mapping_file = self.paths["config"] / "input_file_mapping.json"
        return json.loads(mapping_file.read_bytes())

    def get_paths(self):
        return {dir: self.root / dir for dir in self._subdirs}

    def get_parameters(self):
        params_file = self.paths["config"] / "parameters.json"
        if params_file.exists():
            return json.loads(params_file.read_text())
        else:
            return {}

    def check_files(self):
        if not self.root.exists():
            raise FileNotFoundError(
                f"Could not find the data directory under {self.root}"
            )

        not_found = []
        for f in self._mandatory_files:
            absolute_path = self.root / f
            if not absolute_path.exists():
                not_found.append(f)

        if not_found:
            msg = [
                f'Could not find the following files or directories in "{self.root}":'
            ]
            msg += [f"- {file}" for file in not_found]
            raise FileNotFoundError("\n".join(msg))
