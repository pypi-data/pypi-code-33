"""
Base algorithm

The Algorithm class can be extend to implement useful graph algorithms.
"""


import logging
import time
import sys


def execute(data, task=None, loglevel=logging.DEBUG):
    """
    Runs the spring embedder for the given data.

    :param data: hierarchic (json-like) map of input data
    :param task: reference to task object
    :type data: usually a dict object, default is None
    :type task: a Task or a DynamicTask object or None

    This method is needed to run the algorithm as dynamic task.
    """
    instance = Algorithm(data, task, loglevel=loglevel)
    return instance.process()


class Algorithm(object):
    """
    A base class for algorithms.
    """

    def __init__(self, data, task=None, name=None, loglevel=logging.DEBUG):
        """
        Init algorithm base object.

        :param data: hierarchic (json-like) map of input data
        :param task: reference to task object
        :type data: usually a dict object
        :type task: a Task or a DynamicTask object or None
        :type name: name for logging
        :type name: string
        :type loglevel: log level, default is DEBUG
        :type loglevel: logging log level
        """
        self._data = data
        self._task = task
        self._error = False
        self._result = None
        self._current_step = None
        self._message = None
        self._current_progress = None
        self._max_progress = None
        if not name:
            name = str(self.__class__.__name__).strip()
        self._logger = logging.Logger(name, level=loglevel)
        if loglevel is not logging.NOTSET:
            self._setup_console_logger(loglevel)

        self.calc_max_progress()

    def _setup_console_logger(self, loglevel):
        """
        Log to console.
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(loglevel)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def _send_update(self):
        """
        Forward update to task if task is used.
        """
        if self._task:
            self._task.update(self._message, (
                self._current_progress,
                self._max_progress),
                self._current_step)

    def error(self, message):
        """
        Algorithm execution failed.

        :param message: error description
        :type message: usually string
        """
        self._error = True
        self._result = message
        if self._task:
            self._task.error(message)
        else:
            self._logger.error('Error: {}'.format(message))

    def done(self, result):
        """
        Algorithm execution successful.

        :param result: algorithm result
        :type result: usually net as json-like dict
        """
        self._error = False
        self._result = result
        if self._task:
            self._task.done(result)
        else:
            self._logger.info('Result: {}'.format(result))

    def is_success(self):
        """
        Was the algorithm successful?
        """
        return not self._error

    def result(self):
        """
        Result of the algorithm.

        If the algorithm is not finished this is None and
        if the algorithm failed it is the error message.

        For the demo algorithm, the result is (min, sum).
        """
        return self._result

    def is_done(self):
        """
        Is the algorithm complete?
        """
        return self._result is not None

    def log(self, message):
        """
        Logger for algorithm.

        :param message: log message
        :type message: usually a string
        """
        if self._task:
            self._message = message
            self._send_update()
        else:
            self._logger.debug(message)

    def step(self, description):
        """
        Algorithm step started.

        :param description: description of the current algorithm step
        :type message: usually a dict or a string
        """
        if self._task:
            self._current_step = description
            self._send_update()
        else:
            self._logger.info('Step: {}'.format(description))

    def progress(self, current, max):
        """
        Algorithm progress.

        :param current: current progress
        :type current: int value, i.e. 10
        :param max: maximum progress, i.e. end of algorithm
        :type max:  int value, i.e. 100
        """
        if self._task:
            self._current_progress = current
            self._max_progress = max
            self._send_update()
        else:
            self._logger.info('Progress: {} of {}'.format(
                current,
                max))

    def calc_max_progress(self):
        """
        Calculate the necessary small step count for the algorithm.

        This method must be overwritten for algorithms if
        self.do_progress() is used.
        """
        if self._data and 'numbers' in self._data:
            self._max_progress = 2 * len(self._data['numbers'])
        self._current_progress = 0

    def do_progress(self):
        """
        Increment progress by 1.

        Increments the algorithm progress by 1 tick.
        """
        self._current_progress = self._current_progress + 1
        self.progress(self._current_progress, self._max_progress)

    def process(self):
        """
        Main processing method of the algorithm.

        This method must be overwritten by useful algorithms.

        The example implementation finds the minimum and
        calculates the sum of a given number series.
        This method will need more than 2 * len(input) seconds.

        The input data object is stored in self._data.
        """
        if not self._data:
            # input data is necessary
            self._error('Invalid data!')
            return

        if 'numbers' not in self._data:
            # input data is necessary
            self._error('No data!')
            return

        if len(self._data['numbers']) == 0:
            # input data must be at least one value
            self._error('Empty data!')
            return

        numbers = self._data['numbers']
        fast = False
        if 'fast' in self._data:
            fast = bool(self._data['fast'])

        # Enter step 1 of the algorithm: find minimum
        self.step({
            'Description': 'Find minimum of data.',
            'Current': 1,
            'Max': 2,
            })

        min = numbers[0]
        # log the new minimum
        self.log("Current min: {}".format(min))
        for d in numbers:
            if not fast:
                # spend some time to simulate a real algorithm
                time.sleep(1)
            self.do_progress()
            if d < min:
                min = d
                self.log("Current min: {}".format(min))

        # Enter step 2 of the algorithm: calculate the sum
        self.step({
            'Description': 'Sum up data values.',
            'Current': 2,
            'Max': 2,
            })

        sum = 0
        self.log("Current sum: {}".format(sum))
        for d in numbers:
            if not fast:
                time.sleep(1)
            self.do_progress()
            sum = sum + d
            self.log("Current sum: {}".format(sum))

        # algorithm successful done, give the result back
        self.done((min, sum))

        # return the result
        return (min, sum)
