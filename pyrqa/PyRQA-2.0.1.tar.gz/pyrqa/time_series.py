#!/usr/bin/env python

"""
Time Series.
"""

import numpy as np

from pyrqa.exceptions import TimeDelayReconstructionNotSupportedException, \
    UnsupportedDataTypeException

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"

SUPPORTED_DATA_TYPES = (np.dtype('float16'),
                        np.dtype('float32'),
                        np.dtype('float64'))


class TimeSeries(object):
    """
    Time series.
    """

    def __init__(self,
                 data):
        self.data = data

        self.__validate_data_type()

    def __validate_data_type(self):
        """
        Validate the data type of the floating point values.
        """
        if self.data.dtype not in SUPPORTED_DATA_TYPES:
            raise UnsupportedDataTypeException("Data type '%s' is not supported. Please select either numpy data type float16, float32 or float64." % self.data_type)

    @property
    def embedding_dimension(self):
        """
        Embedding dimension.
        """
        return None

    @embedding_dimension.setter
    def embedding_dimension(self,
                            value):
        pass

    @property
    def number_of_vectors(self):
        """
        Number of vectors.
        """
        return None

    @property
    def length(self):
        """
        Length of time series.
        """
        return None

    @property
    def dtype(self):
        """
        Data type of floating point values.
        """
        return  self.data.dtype

    def get_vector(self,
                   idx):
        """
        Get vector from the original time series based on the index given.

        :param idx: Index of vector.
        :return: Vector.
        """
        pass

    def get_vectors(self,
                    start,
                    count):
        """
        Get vectors from the original time series.

        :param start: Start index within the original time series.
        :param count: Number of vectors to be extracted.
        :returns: Extracted vectors.
        :rtype: 1D array.
        """
        pass

    def get_vectors_as_2d_array(self,
                                start,
                                count):
        """
        Get vectors from the original time series as 2D array.

        :param start: Start index within the original time series.
        :param count: Number of vectors to be extracted.
        :returns: Extracted vectors.
        :rtype: 2D array.
        """
        pass

    def get_minimum_and_maximum_vector(self,
                                       start,
                                       count):
        """
        Get the minimum and maximum vector based on the embedding parameters specified.

        :return: Minimum vector, Maximum vector.
        """
        minimum_vector = np.array([np.finfo(self.data.dtype).max for _ in np.arange(self.embedding_dimension)])
        maximum_vector = np.array([np.finfo(self.data.dtype).min for _ in np.arange(self.embedding_dimension)])

        for vector in self.get_vectors_as_2d_array(start, count):
            minimum_vector = np.minimum(minimum_vector, vector)
            maximum_vector = np.maximum(maximum_vector, vector)

        return minimum_vector, maximum_vector


class SingleTimeSeries(TimeSeries):
    """
    Single time series. The reconstruction of vectors is conducted using the time delay method.
    """
    def __init__(self,
                 data,
                 dtype=np.float32,
                 embedding_dimension=2,
                 time_delay=2):
        TimeSeries.__init__(self,
                            np.array(data, dtype=dtype))

        self._dtype = dtype
        self._embedding_dimension = embedding_dimension
        self._time_delay = time_delay

    @property
    def embedding_dimension(self):
        return self._embedding_dimension

    @embedding_dimension.setter
    def embedding_dimension(self,
                            value):
        self._embedding_dimension = value

    @property
    def time_delay(self):
        """
        Time delay for reconstructing vectors from a single time series.
        """
        return self._time_delay

    @time_delay.setter
    def time_delay(self,
                   value):
        self._time_delay = value

    @property
    def length(self):
        return len(self.data)

    @property
    def offset(self):
        """
        Time series offset based on embedding dimension and time delay.
        """
        return (self.embedding_dimension - 1) * self.time_delay

    @property
    def number_of_vectors(self):
        if self.length - self.offset < 0:
            return 0

        return self.length - self.offset

    def get_vector(self,
                   idx):

        vector = np.zeros(self.embedding_dimension,
                          dtype=self._dtype)

        for dim in np.arange(self.embedding_dimension):
            vector[dim] = self.data[idx + (dim * self.time_delay)]

        return vector

    def get_vectors(self, start, count):
        recurrence_vectors = []

        for dim in np.arange(self.embedding_dimension):
            offset = dim * self.time_delay
            recurrence_vectors.append(self.data[(start + offset):(start + offset + count)])

        return np.array(recurrence_vectors,
                        dtype=self._dtype).transpose().ravel()

    def get_vectors_iterator(self,
                             start,
                             count):
        """
        Get vectors from the original time series (iterator).

        :param start: Start index within the original time series.
        :param count: Number of vectors to be extracted.
        :returns: Extracted vectors.
        :rtype: 1D array.
        """
        recurrence_vectors = np.zeros(count * self.embedding_dimension,
                                      dtype=self._dtype)

        for dim in np.arange(self.embedding_dimension):
            offset = dim * self.time_delay

            for idx in np.arange(count):
                recurrence_vectors[idx * self.embedding_dimension + dim] = self.data[start + idx + offset]

    def get_vectors_as_2d_array(self,
                                start,
                                count):
        recurrence_vectors = self.get_vectors(start,
                                              count)

        recurrence_vectors.shape = (np.int(recurrence_vectors.size / self.embedding_dimension),
                                    self.embedding_dimension)

        return recurrence_vectors

    def get_time_series(self, start, count):
        """
        Get sub time series from the original time series.

        :param start: Start index within the original time series.
        :param count: Number of data points to be extracted.
        :returns: Extracted sub time series.
        :rtype: 1D array.
        """
        return self.data[start:start + count + self.offset]


class MultipleTimeSeries(TimeSeries):
    """
    Multiple time series. The vectors are represented by components with the same ID from multiple time series.
    All time series have to have the same length.
    """

    def __init__(self,
                 data,
                 dtype=np.float32):
        """
        :param data: Input data structured as array of columns.
        """
        TimeSeries.__init__(self,
                            np.array(data, dtype=dtype))

        self._dtype = dtype

    @property
    def embedding_dimension(self):
        return self.data.shape[0]

    @property
    def time_delay(self):
        """
        Time delay for reconstructing vectors from a single time series.
        """
        raise TimeDelayReconstructionNotSupportedException("Time delay reconstruction is not supported for 'MultipleTimeSeries'.")

    @property
    def length(self):
        return self.data.shape[1]

    @property
    def offset(self):
        """
        Time series offset based on embedding dimension and time delay.
        """
        raise TimeDelayReconstructionNotSupportedException("Time delay reconstruction is not supported for 'MultipleTimeSeries'.")

    @property
    def number_of_vectors(self):
        return self.data.shape[1]

    def get_vector(self,
                   idx):
        return self.data[:,idx]

    def get_vectors(self,
                    start,
                    count):

        return np.hstack(self.data[:,np.arange(start,
                                               start + count)].transpose(1, 0))

    def get_vectors_as_2d_array(self,
                                start,
                                count):
        return self.data[:, np.arange(start,
                                      start + count)].transpose(1, 0)

    @staticmethod
    def get_time_series():
        """
        Get sub time series from the original time series.
        """
        raise TimeDelayReconstructionNotSupportedException("Time delay reconstruction is not supported for 'MultipleTimeSeries'.")
