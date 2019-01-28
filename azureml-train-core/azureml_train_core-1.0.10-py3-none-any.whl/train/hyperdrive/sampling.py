# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The hyperparameter sampling definitions."""
from abc import ABC

from azureml.exceptions import AzureMLException


class HyperParameterSampling(ABC):
    """Abstract base class for all hyperparameter sampling algorithms.

    It encapsulates the hyperparameter space, the sampling method and additional properties.

    :param sampling_method_name: Name of the sampling method.
    :type sampling_method_name: str
    :param parameter_space: A dictionary containing each parameter and its distribution.
    :type parameter_space: dict
    :param properties: A dictionary with additional properties for the algorithm.
    :type properties: dict
    :param supported_distributions: A list of the supported distribution methods. Default of None indicates all
    distributions are supported.
    :type supported_distributions: set[str]
    """

    def __init__(self, sampling_method_name, parameter_space, properties=None, supported_distributions=None):
        """Initialize HyperParameterSampling.

        :param sampling_method_name: Name of the sampling method.
        :type sampling_method_name: str
        :param parameter_space: A dictionary containing each parameter and its distribution.
        :type parameter_space: dict
        :param properties: A dictionary with additional properties for the algorithm.
        :type properties: dict
        :param supported_distributions: A list of the supported distribution methods. Default of None indicates all
        distributions are supported.
        :type supported_distributions: set[str]
        """
        self._sampling_method_name = sampling_method_name
        self._parameter_space = parameter_space
        self._properties = properties
        self._supported_distributions = supported_distributions
        self._validate_supported_distributions()

    def to_json(self):
        """Return the json of the hyperparameter sampling object.

        :returns: JSON formatted sampling policy.
        :rtype: str
        """
        definition = \
            {
                "name": self._sampling_method_name,
                "parameter_space": self._parameter_space
            }
        if self._properties:
            definition["properties"] = self._properties

        return definition

    def _validate_supported_distributions(self):
        if self._supported_distributions:
            for distribution in self._parameter_space.values():
                if distribution[0] not in self._supported_distributions:
                    msg = "Distribution '{}' not supported. Only [{}] are supported for this sampling method."\
                        .format(distribution[0], ", ".join(self._supported_distributions))
                    raise AzureMLException(msg)


class RandomParameterSampling(HyperParameterSampling):
    """Random hyperparameter space sampling.

    In this sampling space, the parameter value can either be a choice among discrete values
    or distribution over a continuous range for each value,
    like for instance uniform, loguniform, normal, lognormal, etc.
    For example,

    .. code-block:: python

        {
            "init_lr": uniform(0.0005, 0.005),
            "hidden_size": choice(0, 100, 120, 140, 180)
        }

    This will define a search space with two parameters, init_lr and hidden_size.
    The init_lr can have a uniform distribution with 0.0005 as min and 0.005 as max value, and
    the hidden_size one of [80, 100, 120, 140, 180].

    :param parameter_space: A dictionary containing each parameter and its distribution.
                            Key is name of the parameter.
    :type parameter_space: dict
    :param properties: A dictionary with additional properties for the algorithm.
    :type properties: dict
    """

    def __init__(self, parameter_space, properties=None):
        """Initialize RandomParameterSampling.

        :param parameter_space: A dictionary containing each parameter and its distribution.
                                Key is name of the parameter.
        :type parameter_space: dict
        :param properties: A dictionary with additional properties for the algorithm.
        :type properties: dict
        """
        super().__init__("RANDOM", parameter_space, properties)


class GridParameterSampling(HyperParameterSampling):
    """Grid hyperparameter space sampling.

    In this sampling space, the parameter value is only a choice among the discrete values.
    For example,

    .. code-block:: python

        {
          "lr": choice(1, 2, 3),
          "batch": choice(8, 9)
        }

    This will define a search space with two parameters, lr and batch.
    The lr can have one of the values [1, 2, 3 ], and the batch one of [8, 9].

    :param parameter_space: A dictionary containing each parameter and its distribution.
                            Key is name of the parameter.
    :type parameter_space: dict
    """

    def __init__(self, parameter_space):
        """Initialize GridParameterSampling.

        :param parameter_space: A dictionary containing each parameter and its distribution.
                                Key is name of the parameter.
        :type parameter_space: dict
        """
        supported_distributions = {'choice'}
        super().__init__("GRID", parameter_space, supported_distributions=supported_distributions)


class BayesianParameterSampling(HyperParameterSampling):
    """Bayesian hyperparameter space sampling.

    Bayesian sampling tries to intelligently pick the next sample of hyperparameters,
    based on how the previous samples performed, such that the new sample improves
    the reported primary metric.

    Please note that when using Bayesian, the number of concurrent runs has an impact
    on the effectiveness of the tuning process. Typically, a smaller number of concurrent
    runs can lead to better sampling convergence. That is because some runs start without
    fully benefiting from runs that are still running.

    :param parameter_space: A dictionary containing each parameter and its distribution.
                            Key is name of the parameter. Please note that only choice,
                            quniform and uniform are supported for Bayesian optimization.
    :type parameter_space: dict
    """

    def __init__(self, parameter_space):
        """Initialize BayesianParameterSampling.

        :param parameter_space: A dictionary containing each parameter and its distribution.
                                Key is name of the parameter. Please note that only choice,
                                quniform and uniform are supported for Bayesian optimization.
        :type parameter_space: dict
        """
        if parameter_space is None:
            raise AzureMLException("parameter_space cannot be None")

        supported_distributions = {'choice', 'quniform', 'uniform'}
        super().__init__("BayesianOptimization", parameter_space, supported_distributions=supported_distributions)
