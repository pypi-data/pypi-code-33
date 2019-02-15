from .app import FGApp
from .data import FGData
from .io import FilesInput, FilesOutput
from .summary import FGSummary
from .defaults import DEFAULT_APP_DIR, DEFAULT_DATA_ROOT, SUMMARY_KEY
from .utils import str_normalize

from logging import getLogger


class FGProcess(object):
    def __init__(self, app_dir=DEFAULT_APP_DIR, data_dir=DEFAULT_DATA_ROOT):
        self.data = FGData(data_dir)
        self.app = FGApp(app_dir)

        self.parameters = self.app.default_parameters.copy()
        self.parameters.update(self.data.parameters)

        app_name = str_normalize(self.app.application["name"])
        self.logger = getLogger(f"fastgenomics.{app_name}")

        # log the updated parameter values
        info = "\n".join(f"{k}:{v.value}" for k, v in self.parameters.parameter.items())
        self.logger.info(f"Parameters: \n{info}")

        self.input = FilesInput(
            specs=self.app.inputs,
            root=self.data.paths["data"],
            mapping=self.data.input_file_mapping,
        )
        self.output = FilesOutput(
            specs=self.app.outputs,
            root=self.data.paths["output"],
            summary_path=self.data.paths[SUMMARY_KEY] / "summary.md",
        )

        self.summary = FGSummary(
            output=self.output[SUMMARY_KEY], params=self.parameters
        )
