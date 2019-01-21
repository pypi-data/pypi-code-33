# coding: utf-8

"""
    Endpoints

    Endpoints API for different services in SKIL  # noqa: E501

    OpenAPI spec version: 1.2.0-rc1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class EvaluationResultsEntity(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'evaluation': 'str',
        'eval_name': 'str',
        'model_instance_id': 'str',
        'created': 'int',
        'f1': 'float',
        'precision': 'float',
        'recall': 'float',
        'accuracy': 'float',
        'rmse': 'float',
        'auc': 'float',
        'mean_absolute_error': 'float',
        'mean_relative_error': 'float',
        'r2': 'float',
        'eval_id': 'str',
        'eval_version': 'int',
        'binary_threshold': 'float',
        'binary_thresholds': 'str'
    }

    attribute_map = {
        'evaluation': 'evaluation',
        'eval_name': 'evalName',
        'model_instance_id': 'modelInstanceId',
        'created': 'created',
        'f1': 'f1',
        'precision': 'precision',
        'recall': 'recall',
        'accuracy': 'accuracy',
        'rmse': 'rmse',
        'auc': 'auc',
        'mean_absolute_error': 'meanAbsoluteError',
        'mean_relative_error': 'meanRelativeError',
        'r2': 'r2',
        'eval_id': 'evalId',
        'eval_version': 'evalVersion',
        'binary_threshold': 'binaryThreshold',
        'binary_thresholds': 'binaryThresholds'
    }

    def __init__(self, evaluation=None, eval_name=None, model_instance_id=None, created=None, f1=None, precision=None, recall=None, accuracy=None, rmse=None, auc=None, mean_absolute_error=None, mean_relative_error=None, r2=None, eval_id=None, eval_version=None, binary_threshold=None, binary_thresholds=None):  # noqa: E501
        """EvaluationResultsEntity - a model defined in Swagger"""  # noqa: E501

        self._evaluation = None
        self._eval_name = None
        self._model_instance_id = None
        self._created = None
        self._f1 = None
        self._precision = None
        self._recall = None
        self._accuracy = None
        self._rmse = None
        self._auc = None
        self._mean_absolute_error = None
        self._mean_relative_error = None
        self._r2 = None
        self._eval_id = None
        self._eval_version = None
        self._binary_threshold = None
        self._binary_thresholds = None
        self.discriminator = None

        if evaluation is not None:
            self.evaluation = evaluation
        if eval_name is not None:
            self.eval_name = eval_name
        if model_instance_id is not None:
            self.model_instance_id = model_instance_id
        if created is not None:
            self.created = created
        if f1 is not None:
            self.f1 = f1
        if precision is not None:
            self.precision = precision
        if recall is not None:
            self.recall = recall
        if accuracy is not None:
            self.accuracy = accuracy
        if rmse is not None:
            self.rmse = rmse
        if auc is not None:
            self.auc = auc
        if mean_absolute_error is not None:
            self.mean_absolute_error = mean_absolute_error
        if mean_relative_error is not None:
            self.mean_relative_error = mean_relative_error
        if r2 is not None:
            self.r2 = r2
        if eval_id is not None:
            self.eval_id = eval_id
        if eval_version is not None:
            self.eval_version = eval_version
        if binary_threshold is not None:
            self.binary_threshold = binary_threshold
        if binary_thresholds is not None:
            self.binary_thresholds = binary_thresholds

    @property
    def evaluation(self):
        """Gets the evaluation of this EvaluationResultsEntity.  # noqa: E501


        :return: The evaluation of this EvaluationResultsEntity.  # noqa: E501
        :rtype: str
        """
        return self._evaluation

    @evaluation.setter
    def evaluation(self, evaluation):
        """Sets the evaluation of this EvaluationResultsEntity.


        :param evaluation: The evaluation of this EvaluationResultsEntity.  # noqa: E501
        :type: str
        """

        self._evaluation = evaluation

    @property
    def eval_name(self):
        """Gets the eval_name of this EvaluationResultsEntity.  # noqa: E501


        :return: The eval_name of this EvaluationResultsEntity.  # noqa: E501
        :rtype: str
        """
        return self._eval_name

    @eval_name.setter
    def eval_name(self, eval_name):
        """Sets the eval_name of this EvaluationResultsEntity.


        :param eval_name: The eval_name of this EvaluationResultsEntity.  # noqa: E501
        :type: str
        """

        self._eval_name = eval_name

    @property
    def model_instance_id(self):
        """Gets the model_instance_id of this EvaluationResultsEntity.  # noqa: E501


        :return: The model_instance_id of this EvaluationResultsEntity.  # noqa: E501
        :rtype: str
        """
        return self._model_instance_id

    @model_instance_id.setter
    def model_instance_id(self, model_instance_id):
        """Sets the model_instance_id of this EvaluationResultsEntity.


        :param model_instance_id: The model_instance_id of this EvaluationResultsEntity.  # noqa: E501
        :type: str
        """

        self._model_instance_id = model_instance_id

    @property
    def created(self):
        """Gets the created of this EvaluationResultsEntity.  # noqa: E501

        When the evaluation result was created  # noqa: E501

        :return: The created of this EvaluationResultsEntity.  # noqa: E501
        :rtype: int
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this EvaluationResultsEntity.

        When the evaluation result was created  # noqa: E501

        :param created: The created of this EvaluationResultsEntity.  # noqa: E501
        :type: int
        """

        self._created = created

    @property
    def f1(self):
        """Gets the f1 of this EvaluationResultsEntity.  # noqa: E501


        :return: The f1 of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._f1

    @f1.setter
    def f1(self, f1):
        """Sets the f1 of this EvaluationResultsEntity.


        :param f1: The f1 of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._f1 = f1

    @property
    def precision(self):
        """Gets the precision of this EvaluationResultsEntity.  # noqa: E501


        :return: The precision of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._precision

    @precision.setter
    def precision(self, precision):
        """Sets the precision of this EvaluationResultsEntity.


        :param precision: The precision of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._precision = precision

    @property
    def recall(self):
        """Gets the recall of this EvaluationResultsEntity.  # noqa: E501


        :return: The recall of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._recall

    @recall.setter
    def recall(self, recall):
        """Sets the recall of this EvaluationResultsEntity.


        :param recall: The recall of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._recall = recall

    @property
    def accuracy(self):
        """Gets the accuracy of this EvaluationResultsEntity.  # noqa: E501


        :return: The accuracy of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._accuracy

    @accuracy.setter
    def accuracy(self, accuracy):
        """Sets the accuracy of this EvaluationResultsEntity.


        :param accuracy: The accuracy of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._accuracy = accuracy

    @property
    def rmse(self):
        """Gets the rmse of this EvaluationResultsEntity.  # noqa: E501


        :return: The rmse of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._rmse

    @rmse.setter
    def rmse(self, rmse):
        """Sets the rmse of this EvaluationResultsEntity.


        :param rmse: The rmse of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._rmse = rmse

    @property
    def auc(self):
        """Gets the auc of this EvaluationResultsEntity.  # noqa: E501


        :return: The auc of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._auc

    @auc.setter
    def auc(self, auc):
        """Sets the auc of this EvaluationResultsEntity.


        :param auc: The auc of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._auc = auc

    @property
    def mean_absolute_error(self):
        """Gets the mean_absolute_error of this EvaluationResultsEntity.  # noqa: E501


        :return: The mean_absolute_error of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._mean_absolute_error

    @mean_absolute_error.setter
    def mean_absolute_error(self, mean_absolute_error):
        """Sets the mean_absolute_error of this EvaluationResultsEntity.


        :param mean_absolute_error: The mean_absolute_error of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._mean_absolute_error = mean_absolute_error

    @property
    def mean_relative_error(self):
        """Gets the mean_relative_error of this EvaluationResultsEntity.  # noqa: E501


        :return: The mean_relative_error of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._mean_relative_error

    @mean_relative_error.setter
    def mean_relative_error(self, mean_relative_error):
        """Sets the mean_relative_error of this EvaluationResultsEntity.


        :param mean_relative_error: The mean_relative_error of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._mean_relative_error = mean_relative_error

    @property
    def r2(self):
        """Gets the r2 of this EvaluationResultsEntity.  # noqa: E501


        :return: The r2 of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._r2

    @r2.setter
    def r2(self, r2):
        """Sets the r2 of this EvaluationResultsEntity.


        :param r2: The r2 of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._r2 = r2

    @property
    def eval_id(self):
        """Gets the eval_id of this EvaluationResultsEntity.  # noqa: E501

        GUID of the evaluation  # noqa: E501

        :return: The eval_id of this EvaluationResultsEntity.  # noqa: E501
        :rtype: str
        """
        return self._eval_id

    @eval_id.setter
    def eval_id(self, eval_id):
        """Sets the eval_id of this EvaluationResultsEntity.

        GUID of the evaluation  # noqa: E501

        :param eval_id: The eval_id of this EvaluationResultsEntity.  # noqa: E501
        :type: str
        """

        self._eval_id = eval_id

    @property
    def eval_version(self):
        """Gets the eval_version of this EvaluationResultsEntity.  # noqa: E501


        :return: The eval_version of this EvaluationResultsEntity.  # noqa: E501
        :rtype: int
        """
        return self._eval_version

    @eval_version.setter
    def eval_version(self, eval_version):
        """Sets the eval_version of this EvaluationResultsEntity.


        :param eval_version: The eval_version of this EvaluationResultsEntity.  # noqa: E501
        :type: int
        """

        self._eval_version = eval_version

    @property
    def binary_threshold(self):
        """Gets the binary_threshold of this EvaluationResultsEntity.  # noqa: E501


        :return: The binary_threshold of this EvaluationResultsEntity.  # noqa: E501
        :rtype: float
        """
        return self._binary_threshold

    @binary_threshold.setter
    def binary_threshold(self, binary_threshold):
        """Sets the binary_threshold of this EvaluationResultsEntity.


        :param binary_threshold: The binary_threshold of this EvaluationResultsEntity.  # noqa: E501
        :type: float
        """

        self._binary_threshold = binary_threshold

    @property
    def binary_thresholds(self):
        """Gets the binary_thresholds of this EvaluationResultsEntity.  # noqa: E501


        :return: The binary_thresholds of this EvaluationResultsEntity.  # noqa: E501
        :rtype: str
        """
        return self._binary_thresholds

    @binary_thresholds.setter
    def binary_thresholds(self, binary_thresholds):
        """Sets the binary_thresholds of this EvaluationResultsEntity.


        :param binary_thresholds: The binary_thresholds of this EvaluationResultsEntity.  # noqa: E501
        :type: str
        """

        self._binary_thresholds = binary_thresholds

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, EvaluationResultsEntity):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
