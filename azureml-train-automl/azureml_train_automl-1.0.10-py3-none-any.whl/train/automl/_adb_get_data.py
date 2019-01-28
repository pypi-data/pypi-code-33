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
        self.sample_weight_valid = data_dictionary.get(
            'sample_weight_valid', None)
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
    return _input_data_model(utilities._format_training_data(**data_dictionary))
