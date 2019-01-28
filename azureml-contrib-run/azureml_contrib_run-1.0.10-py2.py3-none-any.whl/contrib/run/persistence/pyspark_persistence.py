# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""pyspark persistence functions."""
import logging
import os

import jsonpickle

from azureml.contrib.run.persistence import base_persistence

try:
    import pyspark
    from pyspark.ml import Model, PipelineModel
except ImportError as ee:
    pass

module_logger = logging.getLogger(__name__)


def save_model(model, model_path):
    """Save pyspark model.

    :param model:
    :param model_path:
    :return:
    """
    def save_spark_model_file(model, model_path):
        assert (is_spark_model(model))
        model.write().overwrite().save(model_path)

    all_ops = [save_spark_model_file]
    return base_persistence.save_model_generic(model, model_path, all_ops)


def load_model(model_path):
    """Load pyspark model.

    :param model_path:
    :return:
    """
    try:
        model_path = os.path.abspath(model_path)
        out = PipelineModel.load(model_path)
        return out
    except Exception as ee:
        module_logger.warning("Pyspark load model error: {}".format(ee), ee)
        raise


def compute_and_save_modeldata(model, model_path):
    """Save modeldata from model.

    :param model:
    :param model_path:
    :return:
    """
    modeldata = compute_modeldata(model, model_path)
    modeldata_path = base_persistence.create_default_modeldata_path(model_path)
    with open(modeldata_path, "w") as modeldata_fp:
        modeldata_json = jsonpickle.encode(modeldata)
        modeldata_fp.write(modeldata_json)

    return modeldata, modeldata_path


def compute_modeldata(model, model_path):
    """Compute and returns modeldata object.

    :param model:
    :param model_path:
    :return:
    """
    modeldata = {}
    modeldata["modeldata.version"] = "0.0.0"
    modeldata["spark.version"] = pyspark.__version__
    modeldata["spark.uid"] = model.uid

    def get_architecture():
        import platform
        return str(platform.architecture())

    modeldata["architecture"] = get_architecture()
    modeldata["model_path"] = model_path
    # azureml type
    modeldata["azureml.type"] = "azureml.model"
    modeldata["library"] = NAME
    modeldata["handler_name"] = NAME  # used by handlers

    return modeldata


def is_spark_model(model):
    """Return True if spark model.

    :param model:
    :return:
    """
    output = isinstance(model, Model)
    return output


def is_spark_model_from_modeldata(modeldata):
    """Return True if is spark model from modeldata.

    :param modeldata:
    :return:
    """
    return modeldata.get("library") == NAME


NAME = "spark"
