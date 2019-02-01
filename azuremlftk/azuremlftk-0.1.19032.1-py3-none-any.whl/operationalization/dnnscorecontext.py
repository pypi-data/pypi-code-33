import json
import numpy as np
from ftk.constants import PIPELINE_PREDICT_OPERATION

class DnnScoreContext(object):
    """
    A context object for DNN scoring pipeline.
    Currently only predict operation is supported.
    """

    def __init__(self, input_scoring_data=None,
                 pipeline_execution_type=PIPELINE_PREDICT_OPERATION):
        self._input_scoring_data = input_scoring_data
        self._pipeline_execution_type = pipeline_execution_type
        self._init_check()

    @property
    def pipeline_execution_type(self):
        return self._pipeline_execution_type

    @property
    def input_scoring_data(self):
        return self._input_scoring_data

    def _init_check(self):
        """
        Todo: add a check for numerical data. raise ftk specific excpetions.
        """
        if not isinstance(self._input_scoring_data, np.ndarray):
            raise Exception('input_scoring_data should be of type numpy.ndarray.')
        elif self.input_scoring_data.ndim != 3:
            raise Exception('input_scoring_data should be three dimensional numerical array.')
        if self._pipeline_execution_type == PIPELINE_PREDICT_OPERATION:
            if self._input_scoring_data is None:
                raise Exception('please provide input scoring data for pipeline execution type ' + self._pipeline_execution_type)
        else:
            raise Exception('unsupported execution type ' + self._pipeline_execution_type)

    def to_json(self):
        attribute_dict = {}
        attribute_dict['pipeline_execution_type'] = self._pipeline_execution_type

        for attribute_key in ['input_scoring_data']:
            if getattr(self, attribute_key) is not None:
                attr_to_list = getattr(self, attribute_key).tolist()
                attribute_dict[attribute_key] = json.dumps(attr_to_list)
            else:
                attribute_dict[attribute_key] = None
        return json.dumps(attribute_dict)

    @classmethod
    def construct_from_json(cls, json_str):
        dict_obj = json.loads(json_str)
        if dict_obj['input_scoring_data'] is not None:
            score_data_json = dict_obj['input_scoring_data']
            score_data_list = json.loads(score_data_json)
            dict_obj['input_scoring_data'] = np.array(score_data_list)

        return cls(**dict_obj)

    def equals(self, other):
        """
        Need to test.
        """
        if not self.pipeline_execution_type == other.pipeline_execution_type:
            return False
        if not self.input_scoring_data.equals(other.input_scoring_data):
            return False
        return True




