from alcathous.algorithms.abstractalgorithm import AbstractAlgorithm


class Minimum(AbstractAlgorithm):
    """
    The minimum value of all valid data points within the time window.
    """

    def _process(self, time_from, time_to):
        self._logger.info("{} - average for '{} s' to '{} s'.".format(self._topic, time_from, time_to))
        sum_values = 0
        count = 0
        minimum = None
        with self._lock_data_set:
            self._logger.info("{} - acquired lock".format(self._topic))
            for timestamp, value in reversed(self._data_set.items()):
                self._logger.info("{} - timestamp '{} s'; value '{}'.".format(self._topic, timestamp, value))
                if time_from > timestamp:
                    self._logger.info("{} - time_from > timestamp".format(self._topic))
                    break
                elif timestamp <= time_to:
                    try:
                        minimum = min(minimum, value)
                    except TypeError:
                        minimum = value
                    count = count + 1
        self._logger.info("{} - sum: {}; count: {}.".format(self._topic, sum_values, count))
        if count == 0:
            raise ValueError
        return minimum

    def execution_points_estimation(self):
        return int(self._time_window)
