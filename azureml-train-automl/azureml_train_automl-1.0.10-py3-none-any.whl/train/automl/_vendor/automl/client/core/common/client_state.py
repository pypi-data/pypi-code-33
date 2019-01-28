# Copyright (c) 2017 Microsoft Corporation.  All rights reserved.
"""Client State Module."""
import copy

import numpy as np

from automl.client.core.common import constants
from automl.client.core.common import metrics


class IterationConfig(object):
    """
    Configuration for an iteration.

    Includes a pipeline hash and a training percent.
    """

    def __init__(self, pipeline_id, training_percent):
        """Create an iteration configuration."""
        self.pipeline_id = pipeline_id
        self.training_percent = training_percent

    @staticmethod
    def from_dict(d):
        """
        Create an iteration configuration from a dictionary.

        :param d: Dictionary to use.
        :return: The initialized iteration configuration
        """
        d_copy = copy.deepcopy(d)
        ret = IterationConfig(None, None)
        ret.__dict__ = d_copy
        return ret

    def to_dict(self):
        """Create a dictionary from an IterationConfig."""
        d = copy.deepcopy(self.__dict__)
        return d


class IterationInfo(object):
    """Iteration information object."""

    def __init__(self, pipeline_id, training_percent, score,
                 predicted_time, predicted_metrics, actual_time):
        """Create an iteration information object."""
        self.config = IterationConfig(pipeline_id, training_percent)
        self.score = score
        self.predicted_time = predicted_time
        self.predicted_metrics = predicted_metrics
        self.actual_time = actual_time

    @staticmethod
    def from_dict(d):
        """
        Create an iteration info object from a dictionary.

        :param d: The dictionary to use.
        :return: An iteration info object.
        """
        d_copy = copy.deepcopy(d)
        d_copy['config'] = IterationConfig.from_dict(d_copy['config'])
        ret = IterationInfo(None, None, None, None, None, None)
        ret.__dict__ = d_copy
        return ret

    def to_dict(self):
        """Create a dictionary from an IterationInfo."""
        d = copy.deepcopy(self.__dict__)
        d['config'] = d['config'].to_dict()
        return d


class ClientState(object):
    """Tracks the history of a client's optimization loop."""

    def __init__(self, metric, task):
        """Create a client state object."""
        self._iteration_infos = []
        self._has_predicted_times = False
        self._metric = metric
        self._task = task

    @staticmethod
    def from_dict(d):
        """
        Create a client state object from a dictionary.

        :param d: The dictionary to use.
        :return: A client state object.
        """
        d_copy = copy.deepcopy(d)
        d_copy['_iteration_infos'] = [IterationInfo.from_dict(ii) for ii
                                      in d_copy['_iteration_infos']]

        ret = ClientState(None, None)
        ret.__dict__ = d_copy
        return ret

    def to_dict(self):
        """Create a dictionary from a ClientState."""
        d = copy.deepcopy(self.__dict__)
        d['_iteration_infos'] = [ii.to_dict() for ii in d['_iteration_infos']]
        return d

    def pipeline_hashes(self):
        """Return a list of pipeline hashes."""
        return [i.config.pipeline_id for i in self._iteration_infos]

    def pipeline_training_percents(self):
        """Return a list of pipeline training percents."""
        return [i.config.training_percent for i in self._iteration_infos]

    def iteration_configs(self):
        """Return a list of iteration configurations."""
        return [i.config for i in self._iteration_infos]

    def iteration_infos(self):
        """Return a list of iteration information objects."""
        return self._iteration_infos

    def _clip(self, score):
        if (self._metric in constants.Metric.CLIPS_POS or
                self._metric in constants.Metric.CLIPS_NEG):
            score = np.clip(
                score,
                constants.Metric.CLIPS_NEG.get(self._metric, None),
                constants.Metric.CLIPS_POS.get(self._metric, None))
        return score

    def optimization_scores(self, clip=True, filter_training_percent=None):
        """Return a list of scores for the metric being optimized."""
        if filter_training_percent:
            vals = [float(ii.score[self._metric]) for ii in
                    self._iteration_infos if ii.config.training_percent ==
                    filter_training_percent]
        else:
            vals = [float(ii.score[self._metric]) for ii in
                    self._iteration_infos]
        if clip:
            vals = [self._clip(x) for x in vals]
        return vals

    def all_scores(self):
        """Return a list of all scores."""
        return [ii.score for ii in self._iteration_infos]

    def all_predicted_metrics(self):
        """Return a list of all predicted metircs."""
        return [ii.predicted_metrics for ii in self._iteration_infos]

    def training_times(self):
        """Return a tuple of (predicted times, actual times)."""
        return (self.predicted_times(), self.actual_times())

    def predicted_times(self):
        """Return a list of predicted times."""
        return [ii.predicted_time for ii in self._iteration_infos] \
            if self._has_predicted_times else []

    def actual_times(self):
        """Return a list of actual times."""
        return [ii.actual_time for ii in self._iteration_infos]

    def update(self, pid, score, predicted_time, actual_time,
               predicted_metrics=None, training_percent=100):
        """Add a new pipeline result.

        :param pid: Pipeline id (hash).
        :param score: A dict of results from validation set.
        :param predicted_time: The pipeline training time predicted
            by the server.
        :param actual_time: The actual pipeline training time.
        :param predicted_metrics: A dict of string to flow representing
            the predicted metrics for the pipeline
        :param training_percent: The training percent that was used.
        """
        if predicted_time:
            self._has_predicted_times = True

        self._iteration_infos.append(
            IterationInfo(pid, training_percent, score,
                          predicted_time, predicted_metrics, actual_time))

    def get_best_pipeline_index(self):
        """Return the best pipeline index."""
        if np.isnan(self.optimization_scores()).all():
            return None
        objective = metrics.minimize_or_maximize(self._metric, self._task)
        if objective == 'maximize':
            return np.nanargmax(self.optimization_scores())
        else:
            return np.nanargmin(self.optimization_scores())

    def get_cost_stats(self):
        """Return the cost statistics used to evaluate performance of the cost model."""
        ret = {}
        actual_times = self.actual_times()
        predicted_times = self.predicted_times()

        if actual_times:
            ret['avg_pipeline_time'] = np.mean(actual_times)

        if predicted_times and actual_times:
            errors = (np.array(predicted_times) -
                      np.array(actual_times))
            ret['RMSE'] = np.sqrt(np.mean(np.square(errors)))
            ret['errors'] = errors.tolist()

        return ret
