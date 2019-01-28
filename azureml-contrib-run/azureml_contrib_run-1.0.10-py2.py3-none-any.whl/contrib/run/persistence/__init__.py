# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init for standard persistence functions."""
import logging

import jsonpickle
from azureml.contrib.run.persistence.handlers_store import HandlersStore, ModelHandler, ModeldataHandler

module_logger = logging.getLogger(__name__)

jsonpickle.set_encoder_options('simplejson', indent=2)

try:
    import jsonpickle.ext.numpy as jsonpickle_numpy

    jsonpickle_numpy.register_handlers()
except ImportError:
    module_logger.debug("Numpy is not available - could not register serialization handlers")


def experimental(fn):
    """Experimental decorator."""
    def wrapper(*args, **kwargs):
        module_logger.warning("Persistence functions are experimental: {}".format(fn))
        output = fn(*args, **kwargs)
        return output

    return wrapper


# modeldata components
modeldata_handlers_store = HandlersStore()
# model components
model_handlers_store = HandlersStore()

try:
    from azureml.contrib.run.persistence import sklearn_persistence

    first_party_modeldata_handlers = [
        ModeldataHandler(sklearn_persistence.NAME, sklearn_persistence.is_sklearn_model,
                         sklearn_persistence.compute_and_save_modeldata)
    ]
    for handler in first_party_modeldata_handlers:
        modeldata_handlers_store.prepend_handler(handler)

    first_party_model_handlers = [
        ModelHandler(sklearn_persistence.NAME, sklearn_persistence.is_sklearn_model, sklearn_persistence.save_model,
                     sklearn_persistence.load_model)
    ]
    for handler in first_party_model_handlers:
        model_handlers_store.prepend_handler(handler)

except ImportError as ee:
    module_logger.warning("persistence import error", ee)

# Third party components
try:
    from azureml.contrib.run.persistence import pyspark_persistence

    modeldata_handlers_store.append_handler(
        ModeldataHandler(pyspark_persistence.NAME, pyspark_persistence.is_spark_model,
                         pyspark_persistence.compute_and_save_modeldata)
    )
except ImportError as ee:
    module_logger.warning("Pyspark is not found in environment. Skipping handler registration.")

try:
    from azureml.contrib.run.persistence import sklearn_persistence

    model_handlers_store.append_handler(
        ModelHandler(pyspark_persistence.NAME, pyspark_persistence.is_spark_model, pyspark_persistence.save_model,
                     pyspark_persistence.load_model)
    )
except ImportError as ee:
    pass
