# coding: utf-8

from collections import OrderedDict
from pathlib import Path
import textwrap
from logging import getLogger

from .defaults import SUMMARY_KEY

logger = getLogger("fastgenomics.common")


class Files(object):
    def __getitem__(self, key):
        if key not in self.files:
            raise KeyError(f'Key "{key}" not defined in manifest.json of the App')
        else:
            return self.files[key]

    def __contains__(self, key):
        return key in self.files

    def __repr__(self):
        output = "Files:\n"
        for file in self.files.values():
            output += textwrap.indent(file.__repr__(), "  ") + "\n"
        return output

    def keys(self):
        return self.files.keys()


class FilesInput(Files):
    def __init__(self, specs, root, mapping):
        self.files = OrderedDict()
        for name, spec in specs.items():
            path = None
            isoptional = "optional" in spec and spec["optional"]
            if name in mapping:
                path = Path(root) / mapping[name]
                if not path.exists():
                    raise FileNotFoundError(f"File {name}: not found under {path}")
            elif isoptional:
                path = None
            else:
                raise KeyError(
                    f'Non-optional file "{name}" missing from input_file_mapping.json'
                )
            self.files[name] = FileInput(
                name=name,
                type=spec["type"],
                usage=spec["usage"],
                path=path,
                optional=isoptional,
            )

        not_in_manifest = set(mapping) - set(specs)
        if not_in_manifest:
            logger.warning(
                f"Ignoring files defined in input_file_mapping.json: {not_in_manifest}"
            )

        logger.debug(f"Files found in the manifest: {list(mapping)}")
        logger.debug(f"Files found in the input_file_mapping.json: {list(specs)}")


class FilesOutput(Files):
    def __init__(self, specs, root, summary_path):
        self.files = OrderedDict()
        for name, spec in specs.items():
            self.files[name] = FileOutput(
                name=name,
                type=spec["type"],
                usage=spec["usage"],
                path=Path(root) / spec["file_name"],
            )
        self.files[SUMMARY_KEY] = FileOutput(
            name="summary", type="summary", usage="Summary file", path=summary_path
        )


class File(object):
    def __init__(self, name, type, usage, path):
        self.name = name
        self.type = type
        self.usage = usage
        self.path = path

    def __repr__(self):
        output = [f'"{arg.capitalize()}": {val}' for arg, val in vars(self).items()]
        return "\n".join(output)


class FileInput(File):
    def __init__(self, name, type, usage, path, optional=False):
        super().__init__(name, type, usage, path)
        self.optional = optional

    def __repr__(self):
        return "\n".join(
            [super().__repr__(), "IO type: Input", f"Optional: {self.optional}"]
        )


class FileOutput(File):
    def __repr__(self):
        return "\n".join([super().__repr__(), "IO type: Output"])
