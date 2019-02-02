#!/usr/bin/env python

"""
Settings
"""

import os

import numpy as np

from scipy.spatial.distance import minkowski, \
    euclidean, \
    chebyshev

from pyrqa.metric import TaxicabMetric, \
    EuclideanMetric, \
    MaximumMetric
from pyrqa.neighbourhood import FixedRadius, \
    FAN

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"

DTYPE_TO_CLASS_MAPPING = {np.dtype('float16'): np.float16,
                          np.dtype('float32'): np.float32,
                          np.dtype('float64'): np.float64}


class Settings(object):
    """
    Settings of recurrence analysis computations.

    :ivar time_series: Time series to be analyzed.
    :ivar similarity_measure: Similarity measure, e.g., EuclideanMetric.
    :ivar neighbourhood: Neighbourhood for detecting neighbours, e.g., FixedRadius(1.0).
    :ivar theiler_corrector: Theiler corrector.
    :ivar config_file_path: Path to configuration file that specifies the names of the kernel files.
    """

    def __init__(self,
                 time_series,
                 similarity_measure=EuclideanMetric,
                 neighbourhood=FixedRadius(),
                 theiler_corrector=1):
        self.time_series = time_series
        self.similarity_measure = similarity_measure
        self.neighbourhood = neighbourhood
        self.theiler_corrector = theiler_corrector

    @property
    def base_path(self):
        """
        Base path of the project.
        """

        return os.path.dirname(os.path.abspath(__file__))

    @property
    def is_matrix_symmetric(self):
        """
        Is the recurrence matrix symmetric?
        """

        return self.similarity_measure.is_symmetric() and not isinstance(self.neighbourhood, FAN)

    @property
    def maximum_phase_space_diameter(self):
        """
        Maximum phase space diameter, depending on the similarity measure applied.
        """

        minimum_vector, \
            maximum_vector = self.time_series.get_minimum_and_maximum_vector(0,
                                                                             self.time_series.number_of_vectors)

        if self.similarity_measure == TaxicabMetric:
            return minkowski(minimum_vector, maximum_vector, 1)

        if self.similarity_measure == EuclideanMetric:
            return euclidean(minimum_vector, maximum_vector)

        if self.similarity_measure == MaximumMetric:
            return chebyshev(minimum_vector, maximum_vector)

    @property
    def diagonal_kernel_name(self):
        """
        Get name of the kernel function to detect the diagonal lines.

        :rtype: String.
        """

        if self.is_matrix_symmetric:
            return "detect_diagonal_lines_symmetric"

        return "detect_diagonal_lines"

    @property
    def kernels_sub_dir(self):
        """
        Get the path of the kernel sub directory.

        :rtype: String.
        """

        return self.similarity_measure.name

    @property
    def radius(self):
        """
        Get radius of neighbourhood converted into dtype of time series.
        """

        return self.dtype(self.neighbourhood.radius)

    @property
    def dtype(self):
        """
        Floating point data type for the time series.
        """

        return DTYPE_TO_CLASS_MAPPING[self.time_series.data.dtype]

    @staticmethod
    def clear_buffer_kernel_name(data_type):
        """
        Get name of the kernel function used to clear a buffer.

        :param data_type: Data type that is used to represent the data values.
        :return: Name of clear buffer kernel.
        :rtype: String.
        """

        return "clear_buffer_%s" % data_type.__name__

    def validate_grid_edge_length(self,
                                  grid_edge_length):
        """
        Validate the edge length of the uniform grid that partitions the embedding space.

        :param grid_edge_length: Grid edge length.
        :return: Validated grid edge length.
        """

        if not grid_edge_length or grid_edge_length < 2 * self.neighbourhood.radius:
            return 2 * self.neighbourhood.radius

        return grid_edge_length

    def __str__(self):
        return "Recurrence Analysis Settings\n" \
               "----------------------------\n" \
               "Similarity measure: %s\n" \
               "Neighbourhood: %s\n" \
               "Theiler corrector: %d\n" \
               "Matrix symmetry: %r\n" % (self.similarity_measure.__name__,
                                          self.neighbourhood,
                                          self.theiler_corrector,
                                          self.is_matrix_symmetric)
