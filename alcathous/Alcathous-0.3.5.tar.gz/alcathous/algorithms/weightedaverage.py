from alcathous.algorithms.abstractalgorithm import AbstractAlgorithm


class WeightedAverage(AbstractAlgorithm):
    """
    The weighted average of all valid data points within the time window. The weight is the inverse time difference
    to the time_to time stamp.
    """

    def _process(self, time_from, time_to):
        self._logger.info("{} - weighted average for '{} s' to '{} s'.".format(self._topic, time_from, time_to))
        sum_weighted_values = 0
        weighted_count = 0
        with self._lock_data_set:
            self._logger.info("{} - acquired lock".format(self._topic))
            for timestamp, value in reversed(self._data_set.items()):
                if time_from > timestamp:
                    self._logger.info("{} - timestamp '{} s'; value '{}'.".format(self._topic, timestamp, value))
                    break
                elif timestamp <= time_to:
                    weight = timestamp - time_from
                    sum_weighted_values = sum_weighted_values + value * weight
                    weighted_count = weighted_count + weight
        self._logger.info("{} - weighted-sum: {}; weighted-count: {}.".
                  format(self._topic, sum_weighted_values, weighted_count))
        try:
            wavg = sum_weighted_values / weighted_count
        except ZeroDivisionError:
            raise ValueError
        return wavg

    def execution_points_estimation(self):
        return int(self._time_window * 1.1)
