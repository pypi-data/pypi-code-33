# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definition of Realtime AI model."""
import tempfile
import os
import json
import shutil
from azureml.contrib.brainwave.pipeline.abstract_stage import StageEncoder
from azureml.core import __version__
import sys
import tensorflow as tf


class ModelDefinition(object):
    """Definition of Realtime AI model.

    You should create a ModelDefinition, append stages to the pipeline
    and then call save. You can then register the file created in that
    location to Model Management and use it to deploy a webservice.
    """

    def __init__(self):
        """Create Model Definition."""
        self.pipeline = []
        self.environment = {"python_version": sys.version, "tensorflow_version": tf.__version__,
                            "package_version": __version__}

    def json_dict(self):
        """Encode information about the pipeline.

        :return: json_dict for encoding to manifest file.
        """
        return {"pipeline": self.pipeline, "environment": self.environment}

    def save(self, model_definition_path: str):
        """Save model definition file.

        To deploy a realtime model, you must upload the created file as a model.

        :param model_definition_path: Path for the model definition to be written to.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            for stage in self.pipeline:
                stage._write_data(tmpdir)
            with open(os.path.join(tmpdir, 'manifest.json'), 'w') as f:
                json.dump(self, f, cls=StageEncoder, sort_keys=True)
            shutil.make_archive(model_definition_path, format='zip', root_dir=tmpdir)
            shutil.move(model_definition_path + ".zip", model_definition_path)
