import json
from ftk.time_series_data_frame import TimeSeriesDataFrame
from ftk.forecast_data_frame import ForecastDataFrame

class ScoreContext(object):
    """
    .. py:class:: ScoreContext
    Class for holding input information to web service scoring.

    :param input_training_data_tsdf:
        Input data for model training.
    :type input_training_data_tsdf: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

    :param input_scoring_data_fcdf:
        Input data to predict on.
    :type input_scoring_data_fcdf:
    :class:`ftk.forecast_data_frame.ForecastDataFrame`

    :param pipeline_execution_type:
        Web service scoring mode.
        Available options are the following:
        * ```train_predict```: first fit the pipeline on the training data,
        then predict on ```input_scoring_data_fcdf```.
        * ```train_only```: only fit the pipeline on the training data.
        * ```predict_only```: only predict on ```input_scoring_data_fcdf```. The
        pipeline deployed to the web service must be fitted.
    :type pipeline_execution_type: str
    """

    def __init__(self, input_training_data_tsdf=None,
                 input_scoring_data_fcdf=None,
                 pipeline_execution_type='train_predict',
                 fit_params=None):
        self._input_training_data_tsdf = input_training_data_tsdf
        self._input_scoring_data_fcdf = input_scoring_data_fcdf
        self._pipeline_execution_type = pipeline_execution_type
        self.fit_params = fit_params
        self._init_check()

    @property
    def pipeline_execution_type(self):
        return self._pipeline_execution_type

    @property
    def input_training_data_tsdf(self):
        return self._input_training_data_tsdf

    @property
    def input_scoring_data_fcdf(self):
        return self._input_scoring_data_fcdf

    @property
    def fit_params(self):
        return self._fit_params

    @fit_params.setter
    def fit_params(self, val):
        if val is None:
            self._fit_params = val
        else:
            if not isinstance(val, dict):
                raise Exception('The value of the fit_params argument needs '
                                'to be a dictionary.')
            self._fit_params = val

    def _init_check(self):
        if self._pipeline_execution_type == 'train_predict':
            if self._input_scoring_data_fcdf is None \
                    or self._input_training_data_tsdf is None:
                raise Exception('please provide both input training and '
                                'scoring data for pipeline execution type '
                                'train_predict.')

        elif self._pipeline_execution_type == 'train_only':
            if self._input_training_data_tsdf is None:
                raise Exception('please provide input training data '
                                'for pipeline execution type train_only.')

        elif self._pipeline_execution_type == 'predict_only':
            if self._input_scoring_data_fcdf is None:
                raise Exception('please provide input scoring data '
                                'for pipeline execution type predict_only.')

    def to_json(self):
        """
        .. py:method:: to_json
        Convert the ScoreContext object to json string.

        :return: The json string representation of the ScoreContext object.
        :rtype: str
        """

        attribute_dict = {}

        attribute_dict['pipeline_execution_type'] \
            = self.pipeline_execution_type
        attribute_dict['fit_params'] = json.dumps(self.fit_params)

        for attribute_key in ['input_training_data_tsdf',
                              'input_scoring_data_fcdf']:
            if getattr(self, attribute_key) is not None:
                attribute_dict[attribute_key] = getattr(self, attribute_key).\
                    to_json()
            else:
                attribute_dict[attribute_key] = None
        return json.dumps(attribute_dict)

    @classmethod
    def construct_from_json(cls, json_str):
        """
        .. py:method:: construct_from_json
        Construct the ScoreContext object from json string.

        :param json_str:
            The input json string for ScoreContext object construction.
        :type json_str: str

        :return: The ScoreContext constructed from the input json string.
        :rtype: ScoreContext
        """

        dict_obj = json.loads(json_str)

        if dict_obj['input_training_data_tsdf'] is not None:
            dict_obj['input_training_data_tsdf'] = \
                TimeSeriesDataFrame.construct_from_json(
                    dict_obj['input_training_data_tsdf'])
        if dict_obj['input_scoring_data_fcdf'] is not None:
            dict_obj['input_scoring_data_fcdf'] = \
                ForecastDataFrame.construct_from_json(
                    dict_obj['input_scoring_data_fcdf'])
        if dict_obj['fit_params'] is not None:
            dict_obj['fit_params'] = json.loads(dict_obj['fit_params'])
        return cls(**dict_obj)

    def equals(self, other):
        """
        .. py:method:: equals
        Check whether two ScoreContext objects are equal. This is designed to
        be used in unit tests.
        """
        if not self.pipeline_execution_type == other.pipeline_execution_type:
            return False
        if not self.input_training_data_tsdf.equals(
                other.input_training_data_tsdf):
            return False
        if not self.input_scoring_data_fcdf.equals(
                other.input_scoring_data_fcdf):
            return False
        if not self.fit_params == other.fit_params:
            return False

        return True


















