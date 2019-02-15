import jsonschema
import json
from pathlib import Path

from .defaults import DEFAULT_APP_DIR
from .parameters import FGParameters


class FGApp(object):
    # files that are checked for existence that are not otherwise
    # explicitly used by the FGApp
    _mandatory_files = ["LICENSE", "LICENSE-THIRD-PARTY", "manifest.json"]

    def __init__(self, app_dir=DEFAULT_APP_DIR):
        if isinstance(app_dir, str):
            app_dir = Path(app_dir)

        self.app_dir = app_dir
        self.check_files()

        self.manifest = self.get_manifest()
        self.application = self.manifest["application"]
        self.default_parameters = FGParameters(self.application["parameters"])
        self.app_type = self.application["type"]
        self.inputs = self.application["input"]
        self.outputs = self.application["output"]
        assert self.app_type in ["Calculation", "Visualization"]

    def get_manifest(self):
        manifest_file = self.app_dir / "manifest.json"
        manifest = json.loads(manifest_file.read_bytes())
        check_manifest(manifest)
        return manifest

    def check_files(self):
        if not self.app_dir.exists():
            raise FileNotFoundError(f"Could not find the App directory {self.app_dir}")

        not_found = []
        for f in self._mandatory_files:
            absolute_path = self.app_dir / f
            if not absolute_path.exists():
                not_found.append(f)

        if not_found:
            msg = [f'Could not find the following files in "{self.app_dir}":']
            msg += [f"- {file}" for file in not_found]
            raise FileNotFoundError("\n".join(msg))


def check_manifest(config: dict):
    """
    Asserts that the manifest (``manifest.json``) matches our JSON-Schema.
    If not a :py:exc:`jsonschema.ValidationError` will be raised.
    """

    schema_file = Path(__file__).parent / "schemes" / "manifest_schema.json"
    schema = json.loads(schema_file.read_text())
    jsonschema.validate(config, schema)

    input_types = config["application"]["input"]
    output_types = config["application"]["output"]

    def err_msg(x, y):
        return "'{}'-type not supported for {}-operations.".format(x, y)

    if input_types is not None:
        for name, properties in input_types.items():
            if properties["type"] == "output_only":
                raise RuntimeError(err_msg(properties["type"], "input"))

    if output_types is not None:
        for name, properties in output_types.items():
            if properties["type"] == "dataset_manifest":
                raise RuntimeError(err_msg(properties["type"], "output"))
