# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs."""

import os
import sys

WIDTH_ITERATION = 10
WIDTH_PIPELINE = 48
WIDTH_TRAINFRAC = 12
WIDTH_DURATION = 10
WIDTH_METRIC = 10
WIDTH_BEST = 10


class ConsoleInterface(object):
    """Class responsible for printing iteration information to console."""

    def __init__(self, metric, file_handler=None):
        """
        Initialize the object.

        :param metric: str representing which metric is being used to score the pipeline.
        """
        self.metric = metric
        self.metric_pretty = metric
        self.file_handler = file_handler
        if file_handler is None:
            self.file_handler = open(os.devnull, 'w')

        self.columns = [
            'ITERATION',
            'PIPELINE',
            'TRAINFRAC',
            'DURATION',  # 'MESSAGE',
            'METRIC',
            'BEST',
        ]
        self.descriptions = [
            'The iteration being evaluated.',
            'A summary description of the pipeline being evaluated.',
            'Fraction of the training data to train on.',
            'Time taken for the current iteration.',  # 'Error or warning message for the current iteration.',
            'The result of computing %s on the fitted pipeline.' % (self.metric_pretty,),
            'The best observed %s thus far.' % self.metric_pretty,
        ]

        self.widths = [
            WIDTH_ITERATION,
            WIDTH_PIPELINE,
            WIDTH_TRAINFRAC,
            WIDTH_DURATION,
            WIDTH_METRIC,
            WIDTH_BEST
        ]
        self.sep_width = 3
        self.filler = ' '
        self.total_width = sum(self.widths) + (self.sep_width * (len(self.widths) - 1))

    def _format_float(self, v):
        """
        Format float as a string.

        :param v:
        :return:
        """
        if isinstance(v, float):
            return '{:.4f}'.format(v)
        return v

    def _format_int(self, v):
        """
        Format int as a string.

        :param v:
        :return:
        """
        if isinstance(v, int):
            return '%d' % v
        return v

    def print_descriptions(self):
        """
        Print description of AutoML console output.

        :return:
        """
        self.file_handler.write('\n')
        self.file_handler.write(('*' * self.total_width) + '\n')
        for column, description in zip(self.columns, self.descriptions):
            self.file_handler.write(column + ': ' + description + '\n')
        self.file_handler.write(('*' * self.total_width) + '\n')
        self.file_handler.write('\n')

    def print_columns(self):
        """
        Print column headers for AutoML printing block.

        :return:
        """
        self.print_start(self.columns[0])
        self.print_pipeline(self.columns[1], '', self.columns[2])
        self.print_end(self.columns[3], self.columns[4], self.columns[5])

    def print_start(self, iteration=''):
        """
        Print iteration number.

        :param iteration:
        :return:
        """
        iteration = self._format_int(iteration)

        s = iteration.rjust(self.widths[0], self.filler)[-self.widths[0]:] + self.filler * self.sep_width
        self.file_handler.write(s)
        sys.stdout.flush()

    def print_pipeline(self, preprocessor='', model_name='', train_frac=1):
        """
        Format a sklearn Pipeline string to be readable.

        :param preprocessor: string of preprocessor name
        :param model_name: string of model name
        :param train_frac: float of fraction of train data to use
        :return:
        """
        separator = ' '
        if preprocessor is None:
            preprocessor = ''
            separator = ''
        if model_name is None:
            model_name = ''
        combined = preprocessor + separator + model_name
        train_frac = str(self._format_float(train_frac))
        self.file_handler.write(combined.ljust(self.widths[1], self.filler)[:(self.widths[1] - 1)])
        self.file_handler.write(train_frac.ljust(self.widths[2], self.filler)[:(self.widths[2] - 1)])
        sys.stdout.flush()

    def print_end(self, duration="", metric="", best_metric=""):
        """
        Print iteration status, metric, and running best metric.

        :param duration: Status of the given iteration
        :param metric: Score for this iteration
        :param best_metric: Best score so far
        :return:
        """
        metric, best_metric = tuple(map(self._format_float, (metric, best_metric)))
        duration, metric, best_metric = tuple(map(str, (duration, metric, best_metric)))
        s = duration.ljust(self.widths[3], self.filler)
        s += metric.rjust(self.widths[4], self.filler)
        s += best_metric.rjust(self.widths[5], self.filler)
        self.file_handler.write(s + '\n')
        sys.stdout.flush()

    def print_error(self, message):
        """
        Print an error message to the console.

        :param message: Error message to display to user
        :return:
        """
        self.file_handler.write('ERROR: ')
        self.file_handler.write(str(message).ljust(self.widths[1], self.filler) + '\n')
        sys.stdout.flush()
