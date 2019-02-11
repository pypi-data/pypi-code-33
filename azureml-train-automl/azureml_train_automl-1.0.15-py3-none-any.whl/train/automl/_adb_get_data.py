# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.train.automl import utilities
from . import _constants_azureml, _dataprep_utilities, automl, constants


class _input_data_model(object):
    def __init__(self, data_dictionary):
        if (data_dictionary is None):
            data_dictionary = {}
        self.X = data_dictionary.get('X', None)
        self.y = data_dictionary.get('y', None)
        self.X_valid = data_dictionary.get('X_valid', None)
        self.y_valid = data_dictionary.get('y_valid', None)
        self.sample_weight = data_dictionary.get('sample_weight', None)
        self.sample_weight_valid = data_dictionary.get('sample_weight_valid', None)
        self.cv_splits_indices = data_dictionary.get('cv_splits_indices', None)
        self.x_raw_column_names = data_dictionary.get('x_raw_column_names', None)


def get_input_datamodel_from_dataprep_json(dataprep_json):
    """
    Convert dataprep data from json to datamodel.

    :param dataprep_json: The dataprep object in json format.
    :return: The dataprep object in datamodel format.
    """
    if dataprep_json is None:
        raise ValueError("dataprep_json is None")
    dataprep_json = dataprep_json.replace(
        '\\"', '"').replace('\\\\', '\\')  # This is to counter the escape chars added by dataprep
    data_dictionary = _dataprep_utilities.load_dataflows_from_json(
        dataprep_json)
    if data_dictionary is None:
        raise ValueError("data_dictionary is None")

    cv_splits_indices = []
    cv_splits_indices_key = "cv_splits_indices"
    new_dictionary = {}
    for key in data_dictionary:
        if cv_splits_indices_key in key:
            cv_splits_indices.append(data_dictionary[key])
        else:
            new_dictionary[key] = data_dictionary[key]

    if not cv_splits_indices:
        cv_splits_indices = None

    new_dictionary[cv_splits_indices_key] = cv_splits_indices
    return _input_data_model(utilities._format_training_data(**new_dictionary))
