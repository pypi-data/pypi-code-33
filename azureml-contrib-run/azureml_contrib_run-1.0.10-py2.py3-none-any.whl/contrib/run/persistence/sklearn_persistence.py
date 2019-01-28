# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""sklearn functions."""
import jsonpickle
from azureml._file_utils import file_utils
from azureml.exceptions import AzureMLException

from azureml.contrib.run.persistence import base_persistence

try:
    import sklearn
    from sklearn import base
    from sklearn.externals import joblib
except ImportError as ee:
    pass


def save_model(model, model_path):
    """Save model object to path.

    :param model:
    :param model_path:
    :return:
    """
    def save_sklearn_model_file(model, model_path):
        """http://scikit-learn.org/stable/modules/model_persistence.html."""
        assert (isinstance(model, base.BaseEstimator))
        # Add to warning when feature is supported
        print("Sklearn model saved in one architecture may not be compatible in other architecture.")
        file_utils.makedirs_for_file_path(model_path)
        joblib.dump(model, model_path)
        return model_path

    all_ops = [save_sklearn_model_file]
    return base_persistence.save_model_generic(model, model_path, all_ops)[0]


def load_model(model_path):
    """Load model from path.

    :param model_path:
    :return:
    """
    try:
        model = joblib.load(model_path)
        return model
    except Exception as ee:
        message = "Load model error: {}".format(ee)
        raise AzureMLException(message)


def compute_and_save_modeldata(model, model_path, save_strategy="joblib"):
    """Compute modeldata then save file.

    :param model:
    :param model_path:
    :param save_strategy:
    :return:
    """
    modeldata = compute_modeldata(model, model_path, save_strategy)
    modeldata_path = base_persistence.create_default_modeldata_path(model_path)
    with open(modeldata_path, "w") as modeldata_fp:
        modeldata_json = jsonpickle.encode(modeldata)
        modeldata_fp.write(modeldata_json)

    return modeldata, modeldata_path


NAME = "sklearn"


def compute_modeldata(model, model_path, save_strategy):
    """Compute modeldata from model.

    :param model:
    :param model_path:
    :param save_strategy:
    :return:
    """
    modeldata = {}
    modeldata["modeldata.version"] = "0.0.0"
    modeldata["scikit-learn.version"] = sklearn.__version__

    def get_architecture():
        import platform
        return str(platform.architecture())

    modeldata["architecture"] = get_architecture()
    modeldata["model_path"] = model_path
    # azureml type
    modeldata["azureml.type"] = "azureml.model"
    modeldata["scikit-learn.save_strategy"] = save_strategy
    modeldata["library"] = NAME
    modeldata["handler_name"] = NAME  # used by handlers
    modeldata["estimator_type"] = model._estimator_type
    modeldata["estimator_name"] = str(model.__class__)
    # dict of param_name:param_value
    modeldata["input_params"] = model.get_params()

    other_values = model.__dict__.copy()
    for key, _value in modeldata.items():
        if key in other_values:
            del other_values[key]

    modeldata["other_values"] = other_values
    return modeldata


def is_sklearn_model(model):
    """Return True if model is sklearn.

    :param model:
    :return:
    """
    output = isinstance(model, base.BaseEstimator)
    return output


def is_sklearn_model_from_modeldata(modeldata):
    """Return True if modeldata states model is sklearn.

    :param modeldata:
    :return:
    """
    return modeldata.get("library") == NAME
