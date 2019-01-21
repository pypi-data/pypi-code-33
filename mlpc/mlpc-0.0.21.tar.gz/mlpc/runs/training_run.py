import time
from mlpc.entity.code import Code
from mlpc.entity.data import Data
from mlpc.entity.measurement import Measurement
from mlpc.entity.model import Model
from mlpc.entity.parameters import Parameters
from mlpc.entity.plot import Plot
from mlpc.metadata import Metadata
from mlpc.runs.base_run import BaseRun
from mlpc.storage.folderstorage import FolderStorage
from mlpc.utils.log import info
from mlpc.utils.json_object_serializer import serialize_to_json_string
import os


class TrainingRun(BaseRun):
    def __init__(self):
        super().__init__(Metadata())
        self._run_start_timestamp = time.time()
        self._storage = FolderStorage(self.metadata)
        self.data = Data(self._storage)
        self.parameters = Parameters(self._storage)
        self.measurement = Measurement(self._storage)
        self.plot = Plot(self._storage)
        self.model = Model(self._storage)
        self.code = Code(self._storage)

    def start(self):  # TODO Rename to _start().
        info("New training run started.", "Timestamp:", self.metadata.timestamp)
        json_string = serialize_to_json_string(self.metadata)
        with open(os.path.join(self.metadata.run_path, "mlpc_metadata.json"), "x") as metadata_file:
            metadata_file.writelines(json_string)

    def complete(self, produce_report=True):  # TODO: Find a better name
        duration_seconds = time.time() - self._run_start_timestamp
        number_of_files_saved, total_bytes_written = self._storage.get_num_files_and_bytes_of_resources_saved()
        info(
            "Training run completed.",
            "Time elapsed:", str(round(duration_seconds, 3)) + "s.",
            "Resourced saved:", number_of_files_saved, "(" + str(total_bytes_written) + " bytes).",
            "Folder: '" + self._storage.run_abs_path + "'"
        )
        # TODO Produce report
        # TODO Save logging output
