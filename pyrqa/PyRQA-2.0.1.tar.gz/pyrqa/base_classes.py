#!/usr/bin/env python

"""
Collection of abstract classes.
"""

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class BaseSettings(object):
    """
    Base settings.

    :ivar settings: Recurrence analysis settings.
    """

    def __init__(self, settings):
        self.settings = settings


class BaseMatrixRuntimes(object):
    """
    Base matrix runtimes.

    :ivar matrix_runtimes: Computing runtimes.
    """

    def __init__(self, matrix_runtimes):
        self.matrix_runtimes = matrix_runtimes


class BaseRunnable(object):
    """
    Base runnable.
    """

    def run(self):
        """
        Perform computations.
        """

        pass

    def run_single_device(self):
        """
        Perform computations using a single computing device.
        """

        pass

    def run_multiple_devices(self):
        """
        Perform computations using multiple computing devices.
        """

        pass


class BaseVerbose(object):
    """
    Base verbose.

    :ivar verbose: Boolean value indicating the verbosity of print outs.
    """

    def __init__(self, verbose):
        self.verbose = verbose

    def print_out(self, obj):
        """
        Print string if verbose is true.
        """

        if self.verbose:
            print(obj)


class BaseMetric(object):
    """
    Base metric.
    """

    name = 'metric'

    @classmethod
    def is_symmetric(cls):
        """
        Is the metric symmetric?
        """

        return True

    @classmethod
    def get_p(cls):
        """
        Get p value of metric.
        """

        pass

    @classmethod
    def get_distance_time_series(cls,
                                 time_series_x,
                                 time_series_y,
                                 embedding_dimension,
                                 time_delay,
                                 index_x,
                                 index_y):
        """
        Get distance between two vectors (time series representation).

        :param time_series_x: Time series on X axis.
        :param time_series_y: Time series on Y axis.
        :param embedding_dimension: Embedding dimension.
        :param time_delay: Time delay.
        :param index_x: Index on X axis.
        :param index_y: Index on Y axis.
        :returns: Distance between two vectors.
        :rtype: Float value.
        """

        pass

    @classmethod
    def get_distance_vectors(cls,
                             vectors_x,
                             vectors_y,
                             embedding_dimension,
                             index_x,
                             index_y):
        """
        Get distance between two vectors (vectors representation).

        :param vectors_x: Vectors on X axis.
        :param vectors_y: Vectors on Y axis.
        :param embedding_dimension: Embedding dimension.
        :param index_x: Index on X axis.
        :param index_y: Index on Y axis.
        :returns: Distance between two vectors.
        :rtype: Float value.
        """

        pass


class BaseNeighbourhood(object):
    """
    Abstract neighbourhood.
    """

    def contains(self,
                 sample):
        """
        Check whether neighbourhood contains sample object.

        :param sample: Sample object, e.g. distance.
        """

        pass
