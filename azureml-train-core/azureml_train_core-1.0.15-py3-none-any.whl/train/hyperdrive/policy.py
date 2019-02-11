# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The early termination policies.

Early termination policies enable cancelling poor-performing runs before they complete.  A poor-performing run
is one that is not doing as well in comparison to the best-performing run with respect to a primary metric.
"""
from abc import ABC
from azureml.exceptions import TrainingException


class EarlyTerminationPolicy(ABC):
    """Abstract base class for all policies.

    Early termination policies for HyperDrive runs.
    A HyperDrive run wil be cancelled based on this policy.
    """

    def __init__(self, name, properties=None):
        """Initialize an early termination policy.

        :param name: The name of the policy.
        :type name: str
        :param properties: A json serializable object of properties.
        :type properties: dict
        """
        self._name = name
        self._properties = properties

    def to_json(self):
        """Return `dict` of termination policy.

        :returns: JSON formatted termination policy.
        :rtype: str
        """
        termination_policy = {
            "name": self._name,
        }

        if self._properties is not None:
            termination_policy["properties"] = self._properties

        return termination_policy


class BanditPolicy(EarlyTerminationPolicy):
    """BanditPolicy is a termination policy based on slack factor/slack amount and evaluation interval.

    Any run that doesn't fall within slack factor/slack amount of the evaluation metric
    with respect to the best performing run will be terminated.

    For example, consider a Bandit policy with slack_factor=0.2 and evaluation_interval of 100.
    Run X is the currently best performing run with an AUC (performance metric) of 0.8 after 100 iterations.
    Assuming the best AUC reported for a run being Y. Then the value (Y + Y * 0.2) is compared to 0.8, and
    if smaller then the run will be cancelled.

    In addition, the first termination policy evaluation can be delayed for a specific number of sequences.
    In the example if delay_evaluation=200 the first time the policy will be applied is at sequence=200.

    For example, consider a Bandit policy with slack_amount=0.2 and evaluation_interval of 100.
    If Run 3 is the currently best performing run with an AUC (performance metric) of 0.8 after 100 iterations,
    then any run with an AUC less than 0.6 (0.8 - 0.2) after 100 iterations will be terminated.
    In addition, the first termination policy evaluation can be delayed for a specific number of sequences.
    In the example if delay_evaluation=200 the first time the policy will be applied is at sequence=200.
    """

    def __init__(self, evaluation_interval=1, slack_factor=None, slack_amount=None, delay_evaluation=0):
        """Initialize a BanditPolicy with slack factor and evaluation interval.

        :param slack_factor: Slack factor with respect to the best performing experiment run.
        :type slack_factor: float
        :param slack_amount: Slack amount is the exact distance from the best performing run.
        :type slack_amount: float
        :param evaluation_interval: Frequency for applying the policy.
        :type evaluation_interval: int
        :param delay_evaluation: This delays the first policy evaluation for specified number of sequences.
                                 If specified, the policy applies every multiple of evaluation_interval
                                 that is greater than or equal to delay_evaluation.
        :type delay_evaluation: int
        """
        if (slack_factor is None and slack_amount is None) or (slack_factor and slack_amount):
            raise TrainingException("For bandit termination policy, specify either slack factor or slack amount "
                                    "with respect to the best performing run.")

        policy_config = {
            "evaluation_interval": evaluation_interval,
            "delay_evaluation": delay_evaluation
        }

        if slack_factor:
            policy_config["slack_factor"] = slack_factor
        else:
            policy_config["slack_amount"] = slack_amount

        super().__init__("Bandit", policy_config)
        self._slack_factor = slack_factor
        self._evaluation_interval = evaluation_interval
        self._delay_evaluation = delay_evaluation

    @property
    def slack_factor(self):
        """Return slack factor with respect to the best performing training run.

        :return: The slack factor.
        :rtype: float
        """
        return self._slack_factor

    @property
    def evaluation_interval(self):
        """Return evaluation interval value.

        :return: The evaluation interval.
        :rtype: int
        """
        return self._evaluation_interval

    @property
    def delay_evaluation(self):
        """Return the value for number of sequences the first evaluation is delayed.

        :return: The delay evaluation.
        :rtype: int
        """
        return self._delay_evaluation


class MedianStoppingPolicy(EarlyTerminationPolicy):
    """MedianStoppingPolicy is an early termination policy based on running averages of runs' primary metrics.

    The Median Stopping policy computes running averages across all runs and cancels those whose best performance
    is worse than the median of the running averages. Specifically, a run j_k will be canceled at sequence s
    if its best primary metric reported up to sequence s is worse than the median of the running averages
    for sequences 1:s across all runs.

    This policy is inspired from Vizier paper: https://research.google.com/pubs/pub46180.html
    """

    def __init__(self, evaluation_interval=1, delay_evaluation=0):
        """Initialize a MedianStoppingPolicy.

        :param evaluation_interval: Frequency for applying the policy.
        :type evaluation_interval: int
        :param delay_evaluation: This delays the first policy evaluation for specified number of sequences.
                                 If specified, the policy applies every multiple of evaluation_interval
                                 that is greater than delay_evaluation.
        :type delay_evaluation: int
        """
        policy_config = {
            "evaluation_interval": evaluation_interval,
            "delay_evaluation": delay_evaluation
        }

        super().__init__("MedianStopping", policy_config)
        self._evaluation_interval = evaluation_interval
        self._delay_evaluation = delay_evaluation

    @property
    def evaluation_interval(self):
        """Return evaluation interval value.

        :return: The evaluation interval.
        :rtype: int
        """
        return self._evaluation_interval

    @property
    def delay_evaluation(self):
        """Return the value for number of sequences the first evaluation is delayed.

        :return: The delay evaluation.
        :rtype: int
        """
        return self._delay_evaluation


class TruncationSelectionPolicy(EarlyTerminationPolicy):
    """TruncationSelectionPolicy cancels a given percentage of runs at each evaluation interval.

    This policy periodically cancels the given percentage of runs that rank the lowest in terms of
    their performance on the primary metric. The policy strives for fairness in ranking the runs by
    taking into account the observation that model performance tends to improve with training time.
    Thus when ranking a relatively young run, it uses the corresponding (and earlier) performance
    of older runs for comparison. This way, runs are not terminated for having a lower performance
    because they have run for less time than other runs.

    For instance, when evaluating a run at a sequence s, its performance is only compared with other runs'
    performance up to sequence s, even if they reported metrics for sequences greater than s.
    """

    def __init__(self, truncation_percentage, evaluation_interval=1, delay_evaluation=0):
        """Initialize a TruncationSelectionPolicy.

        :param truncation_percentage: The percentage of runs to cancel at each evaluation interval.
        :type truncation_percentage: int
        :param evaluation_interval: Frequency for applying the policy.
        :type evaluation_interval: int
        :param delay_evaluation: This delays the first policy evaluation for specified number of sequences.
                                 If specified, the policy applies every multiple of evaluation_interval
                                 that is greater than delay_evaluation.
        :type delay_evaluation: int
        """
        if type(truncation_percentage) != int:
            raise TrainingException("`truncation_percentage` value should be an int value")

        if truncation_percentage < 1 or truncation_percentage > 99:
            raise TrainingException("`truncation_percentage` value needs to be between 1 and 99.")

        policy_config = {
            "evaluation_interval": evaluation_interval,
            "delay_evaluation": delay_evaluation,
            "truncation_percentage": truncation_percentage,
            "exclude_finished_jobs": False
        }

        super().__init__("TruncationSelection", policy_config)
        self._truncation_percentage = truncation_percentage
        self._evaluation_interval = evaluation_interval
        self._delay_evaluation = delay_evaluation

    @property
    def truncation_percentage(self):
        """Return truncation percentage value.

        :return: The truncation percentage.
        :rtype: int
        """
        return self._truncation_percentage

    @property
    def evaluation_interval(self):
        """Return evaluation interval value.

        :return: The evaluation interval.
        :rtype: int
        """
        return self._evaluation_interval

    @property
    def delay_evaluation(self):
        """Return the value for number of sequences the first evaluation is delayed.

        :return: The delay evaluation.
        :rtype: int
        """
        return self._delay_evaluation


class NoTerminationPolicy(EarlyTerminationPolicy):
    """The NoTerminationPolicy does not apply any early termination policy.

    Each run will execute until completion.
    """

    def __init__(self):
        """Initialize NoTerminationPolicy."""
        super().__init__("Default")
