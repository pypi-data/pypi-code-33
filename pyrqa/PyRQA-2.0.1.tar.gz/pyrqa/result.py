#!/usr/bin/env python

"""
Results.
"""

import json
import numpy as np

from pyrqa.base_classes import BaseSettings, \
    BaseMatrixRuntimes

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class RPResult(BaseSettings,
               BaseMatrixRuntimes):
    """
    Recurrence plot result.

    :ivar recurrence_matrix: Recurrence matrix.
    """

    def __init__(self,
                 settings,
                 matrix_runtimes,
                 recurrence_matrix=np.array([], dtype=np.uint32)):
        BaseSettings.__init__(self, settings)
        BaseMatrixRuntimes.__init__(self, matrix_runtimes)

        self.recurrence_matrix = recurrence_matrix

    @property
    def recurrence_matrix_reverse(self):
        """
        Revert recurrence matrix.

        :return: Reverted recurrence matrix.
        """
        return self.recurrence_matrix[::-1]


class RQAResult(BaseSettings,
                BaseMatrixRuntimes):
    """
    Recurrence quantification analysis result.

    :ivar recurrence_points: Recurrence points array.
    :ivar diagonal_frequency_distribution: Diagonal frequency distribution array.
    :ivar vertical_frequency_distribution: Vertical frequency distribution array.
    :ivar white_vertical_frequency_distribution: White vertical frequency distribution array.
    :ivar min_diagonal_line_length: Minimum diagonal line length.
    :ivar min_vertical_line_length: Minimum vertical line length.
    :ivar min_white_vertical_line_length: Minimum white vertical line length.
    """

    def __init__(self,
                 settings,
                 matrix_runtimes,
                 recurrence_points=np.array([], dtype=np.uint32),
                 diagonal_frequency_distribution=np.array([], dtype=np.uint32),
                 vertical_frequency_distribution=np.array([], dtype=np.uint32),
                 white_vertical_frequency_distribution=np.array([], dtype=np.uint32),
                 min_diagonal_line_length=2,
                 min_vertical_line_length=2,
                 min_white_vertical_line_length=2):
        BaseSettings.__init__(self, settings)
        BaseMatrixRuntimes.__init__(self, matrix_runtimes)

        self.recurrence_points = recurrence_points
        self.diagonal_frequency_distribution = diagonal_frequency_distribution
        self.vertical_frequency_distribution = vertical_frequency_distribution
        self.white_vertical_frequency_distribution = white_vertical_frequency_distribution

        self.min_diagonal_line_length = min_diagonal_line_length
        self.min_vertical_line_length = min_vertical_line_length
        self.min_white_vertical_line_length = min_white_vertical_line_length

    @property
    def number_of_recurrence_points(self):
        """
        :return: Number of recurrence points.
        """
        return np.sum(self.recurrence_points)

    @property
    def recurrence_rate(self):
        """
        :return: Recurrence rate (RR).
         """
        err = np.seterr(all='ignore')
        try:
            return np.float32(self.number_of_recurrence_points) / pow(self.settings.time_series.number_of_vectors, 2)
        finally:
            np.seterr(**err)

    @property
    def average_local_recurrence_rate(self):
        """ Average local recurrence rate. """
        err = np.seterr(all='ignore')
        try:
            return np.float32(np.sum(self.recurrence_points)) / self.settings.number_of_vectors
        finally:
            np.seterr(**err)

    def number_of_diagonal_lines(self, min_length):
        """
        Total number of diagonal lines having a minimum length.

        :param min_length: Minimum diagonal line length.
        :return: Total number of diagonal lines.
        """
        if min_length > 0:
            return np.sum(self.diagonal_frequency_distribution[min_length - 1:])

        return np.uint(0)

    def number_of_diagonal_lines_points(self, min_length):
        """
        Total number of recurrence points that form diagonal lines having a minimum length.

        :param min_length: Minimum diagonal line length.
        :return: Total number of points that form diagonal lines.
        """
        if min_length > 0:
            return np.sum(((np.arange(self.diagonal_frequency_distribution.size) + 1) * self.diagonal_frequency_distribution)[min_length - 1:])

        return np.uint(0)

    @property
    def determinism(self):
        """ Determinism (DET). """
        err = np.seterr(all='ignore')
        try:
            return np.float32(self.number_of_diagonal_lines_points(self.min_diagonal_line_length)) / self.number_of_diagonal_lines_points(1)
        finally:
            np.seterr(**err)

    @property
    def average_diagonal_line(self):
        """ Average diagonal line length (L). """
        err = np.seterr(all='ignore')
        try:
            return np.float32(self.number_of_diagonal_lines_points(self.min_diagonal_line_length)) / self.number_of_diagonal_lines(self.min_diagonal_line_length)
        finally:
            np.seterr(**err)

    @property
    def longest_diagonal_line(self):
        """ Longest diagonal line length (L_max). """
        try:
            return np.uint32(np.max(self.diagonal_frequency_distribution.nonzero()[0]) + 1)
        except ValueError:
            return np.uint(0)

    @property
    def entropy_diagonal_lines(self):
        """ Entropy of diagonal lines (L_entr). """
        entropy_diagonal_lines = np.float(.0)

        if self.min_diagonal_line_length > 0:
            line_lengths = np.array(self.diagonal_frequency_distribution[self.min_diagonal_line_length - 1:], dtype=np.float32)
            non_zero = line_lengths.nonzero()[0]

            if non_zero.size > 0:
                line_lengths = line_lengths[non_zero]
                intermediate_sum = np.sum((line_lengths / self.number_of_diagonal_lines(self.min_diagonal_line_length)) * (np.log(line_lengths / self.number_of_diagonal_lines(self.min_diagonal_line_length))))

                if intermediate_sum != .0:
                    entropy_diagonal_lines -= intermediate_sum
                else:
                    entropy_diagonal_lines += intermediate_sum

        return entropy_diagonal_lines

    @property
    def divergence(self):
        """ Divergence (DIV). """
        err = np.seterr(all='ignore')
        try:
            return np.float32(1) / self.longest_diagonal_line
        finally:
            np.seterr(**err)

    def number_of_vertical_lines(self, min_length):
        """
        Total number of vertical lines having a minimum length.

        :param min_length: Minimum vertical line length.
        :return: Total number of vertical lines.
        """
        if min_length > 0:
            return np.sum(self.vertical_frequency_distribution[min_length - 1:])

        return np.uint(0)

    def number_of_vertical_lines_points(self, min_length):
        """
        Total number of recurrence points that form vertical lines having a minimum length.

        :param min_length: minimum line length.
        :return: Total number of points that form vertical lines.
        """
        if min_length > 0:
            return np.sum(((np.arange(self.vertical_frequency_distribution.size) + 1) * self.vertical_frequency_distribution)[min_length - 1:])

        return np.uint(0)

    @property
    def laminarity(self):
        """ Laminarity (LAM). """
        err = np.seterr(all='ignore')
        try:
            return np.float32(self.number_of_vertical_lines_points(self.min_vertical_line_length)) / self.number_of_vertical_lines_points(1)
        finally:
            np.seterr(**err)

    @property
    def trapping_time(self):
        """ Trapping time (TT). """
        err = np.seterr(all='ignore')
        try:
            return np.float32(self.number_of_vertical_lines_points(self.min_vertical_line_length)) / self.number_of_vertical_lines(self.min_vertical_line_length)
        finally:
            np.seterr(**err)

    @property
    def longest_vertical_line(self):
        """ Longest vertical line length (V_max). """
        try:
            return np.uint(np.max(self.vertical_frequency_distribution.nonzero()[0]) + 1)
        except ValueError:
            return np.uint(0)

    @property
    def entropy_vertical_lines(self):
        """ Entropy of vertical lines (V_entr). """
        entropy_vertical_lines = np.float(.0)

        if self.min_vertical_line_length > 0:
            line_lenghts = np.array(self.vertical_frequency_distribution[self.min_vertical_line_length - 1:], dtype=np.float32)
            non_zero = line_lenghts.nonzero()[0]

            if non_zero.size > 0:
                line_lengths = line_lenghts[non_zero]
                intermediate_sum = np.sum((line_lengths / self.number_of_vertical_lines(self.min_vertical_line_length)) * (np.log(line_lengths / self.number_of_vertical_lines(self.min_vertical_line_length))))

                if intermediate_sum != .0:
                    entropy_vertical_lines -= intermediate_sum
                else:
                    entropy_vertical_lines += intermediate_sum

        return entropy_vertical_lines

    def number_of_white_vertical_lines(self, min_length):
        """
        Total number of white vertical lines having a minimum length.

        :param min_length: Minimum white vertical line length.
        :return: Total number of white vertical lines.
        """
        if min_length > 0:
            return np.sum(self.white_vertical_frequency_distribution[min_length - 1:])

        return np.uint(0)

    def number_of_white_vertical_lines_points(self, min_length):
        """
        Total number of white points that form white vertical lines having a minimum length.

        :param min_length: Minimum white vertical line length.
        :return: Total number of points that form white vertical lines.
        """
        if min_length > 0:
            return np.sum(((np.arange(self.white_vertical_frequency_distribution.size) + 1) * self.white_vertical_frequency_distribution)[min_length - 1:])

        return np.uint(0)

    @property
    def average_white_vertical_line(self):
        """ Average white vertical line length (W). """
        err = np.seterr(all='ignore')
        try:
            return np.float32(self.number_of_white_vertical_lines_points(self.min_white_vertical_line_length)) / self.number_of_white_vertical_lines(self.min_white_vertical_line_length)
        finally:
            np.seterr(**err)

    @property
    def longest_white_vertical_line(self):
        """ Longest vertical line length (V_max). """
        try:
            return np.uint(np.max(self.white_vertical_frequency_distribution.nonzero()[0]) + 1)
        except ValueError:
            return np.uint(0)

    @property
    def entropy_white_vertical_lines(self):
        """ Entropy of white vertical lines (V_entr). """
        entropy_white_vertical_lines = np.float(.0)

        if self.min_white_vertical_line_length > 0:
            line_lenghts = np.array(self.white_vertical_frequency_distribution[self.min_white_vertical_line_length - 1:], dtype=np.float32)
            non_zero = line_lenghts.nonzero()[0]

            if non_zero.size > 0:
                line_lengths = line_lenghts[non_zero]
                intermediate_sum = np.sum((line_lengths / self.number_of_white_vertical_lines(self.min_white_vertical_line_length)) * (np.log(line_lengths / self.number_of_white_vertical_lines(self.min_white_vertical_line_length))))

                if intermediate_sum != .0:
                    entropy_white_vertical_lines -= intermediate_sum
                else:
                    entropy_white_vertical_lines += intermediate_sum

        return entropy_white_vertical_lines

    @property
    def longest_white_vertical_line_inverse(self):
        """ Divergence (DIV). """
        err = np.seterr(all='ignore')
        try:
            return np.float32(1) / self.longest_white_vertical_line
        finally:
            np.seterr(**err)

    @property
    def ratio_determinism_recurrence_rate(self):
        """ Ratio determinism / recurrence rate (DET/RR). """
        err = np.seterr(all='ignore')
        try:
            return self.determinism / self.recurrence_rate
        finally:
            np.seterr(**err)

    @property
    def ratio_laminarity_determinism(self):
        """ Ratio laminarity / determinism (LAM/DET). """
        err = np.seterr(all='ignore')
        try:
            return self.laminarity / self.determinism
        finally:
            np.seterr(**err)

    def indices_by_local_recurrence_rate(self, threshold):
        """
        Indices of recurrence vectors, having a local recurrence rate equal-or-smaller to the threshold.

        :param threshold: local recurrence rate threshold.
        :return: Array of recurrence vector indices.
        """
        local_recurrence_rate = np.float64(self.recurrence_points) / self.settings.number_of_vectors
        return np.nonzero(local_recurrence_rate <= threshold)[0]

    def indices_by_number_of_local_recurrence_points(self, threshold):
        """
        Indices of recurrence vectors, having an equal-or-smaller number of local recurrence points.

        :param threshold: Local recurrence points threshold.
        :returns: Array of recurrence vectors indices.
        """
        return np.nonzero(self.recurrence_points <= threshold)[0]

    def persist_diagonal_frequency_distribution(self, file_path):
        """
        Persist diagonal frequency distribution.

        :param file_path: Path to the output file.
        """
        with open(file_path, 'w') as output:
            for length_index in np.arange(self.diagonal_frequency_distribution.size):
                line = "%d: %d\n" % (length_index + self.min_diagonal_line_length, self.diagonal_frequency_distribution[length_index])
                output.write(line)

    def persist_vertical_frequency_distribution(self, file_path):
        """
        Persist vertical frequency distribution.

        :param file_path: Path to the output file.
        """
        with open(file_path, 'w') as output:
            for length_index in np.arange(self.vertical_frequency_distribution.size):
                line = "%d: %d\n" % (length_index + self.min_vertical_line_length, self.vertical_frequency_distribution[length_index])
                output.write(line)

    def persist_white_vertical_frequency_distribution(self, file_path):
        """
        Persist white vertical frequency distribution.

        :param file_path: Path to the output file.
        """
        with open(file_path, 'w') as output:
            for length_index in np.arange(self.white_vertical_frequency_distribution.size):
                line = "%d: %d\n" % (length_index + self.min_white_vertical_line_length, self.white_vertical_frequency_distribution[length_index])
                output.write(line)

    def to_array(self):
        """ Convert result to numpy array. """
        return np.array([self.min_diagonal_line_length,
                         self.min_vertical_line_length,
                         self.min_white_vertical_line_length,
                         self.recurrence_rate,
                         self.determinism,
                         self.average_diagonal_line,
                         self.longest_diagonal_line,
                         self.divergence,
                         self.entropy_diagonal_lines,
                         self.laminarity,
                         self.trapping_time,
                         self.longest_vertical_line,
                         self.entropy_vertical_lines,
                         self.average_white_vertical_line,
                         self.longest_white_vertical_line,
                         self.longest_white_vertical_line_inverse,
                         self.entropy_white_vertical_lines,
                         self.ratio_determinism_recurrence_rate,
                         self.ratio_laminarity_determinism
                        ])

    def to_json(self):
        """ Convert result to json. """
        return json.dumps({"Minimum diagonal line length (L_min)": self.min_diagonal_line_length,
                           "Minimum vertical line length (V_min)": self.min_vertical_line_length,
                           "Minimum white vertical line length (W_min)": self.min_white_vertical_line_length,
                           "Recurrence rate (RR)": self.recurrence_rate,
                           "Determinism (DET)": self.determinism,
                           "Average diagonal line length (L)": self.average_diagonal_line,
                           "Longest diagonal line length (L_max)": self.longest_diagonal_line,
                           "Divergence (DIV)": self.divergence,
                           "Entropy diagonal lines (L_entr)": self.entropy_diagonal_lines,
                           "Laminarity (LAM)": self.laminarity,
                           "Trapping time (TT)": self.trapping_time,
                           "Longest vertical line length (V_max)": self.longest_vertical_line,
                           "Entropy vertical lines (V_entr)": self.entropy_vertical_lines,
                           "Average white vertical line length (W)": self.average_white_vertical_line,
                           "Longest white vertical line length (W_max)": self.longest_white_vertical_line,
                           "Longest white vertical line length inverse (W_div)": self.longest_white_vertical_line_inverse,
                           "Entropy white vertical lines (W_entr)": self.entropy_white_vertical_lines,
                           "Ratio determinism / recurrence rate (DET/RR)": self.ratio_determinism_recurrence_rate,
                           "Ratio laminarity / determinism (LAM/DET)": self.ratio_laminarity_determinism
                          },
                          sort_keys=False,
                          indent=4,
                          separators=(',', ': '))

    def __str__(self):
        return "RQA Result:\n" \
               "-----------\n" \
               "Minimum diagonal line length (L_min): %d\n" \
               "Minimum vertical line length (V_min): %d\n" \
               "Minimum white vertical line length (W_min): %d\n" \
               "\n" \
               "Recurrence rate (RR): %f\n" \
               "Determinism (DET): %f\n" \
               "Average diagonal line length (L): %f\n" \
               "Longest diagonal line length (L_max): %d\n" \
               "Divergence (DIV): %f\n" \
               "Entropy diagonal lines (L_entr): %f\n" \
               "Laminarity (LAM): %f\n" \
               "Trapping time (TT): %f\n" \
               "Longest vertical line length (V_max): %d\n" \
               "Entropy vertical lines (V_entr): %f\n" \
               "Average white vertical line length (W): %f\n" \
               "Longest white vertical line length (W_max): %d\n" \
               "Longest white vertical line length inverse (W_div): %f\n" \
               "Entropy white vertical lines (W_entr): %f\n" \
               "\n" \
               "Ratio determinism / recurrence rate (DET/RR): %f\n"\
               "Ratio laminarity / determinism (LAM/DET): %f\n"        %  (self.min_diagonal_line_length,
                                                                           self.min_vertical_line_length,
                                                                           self.min_white_vertical_line_length,
                                                                           self.recurrence_rate,
                                                                           self.determinism,
                                                                           self.average_diagonal_line,
                                                                           self.longest_diagonal_line,
                                                                           self.divergence,
                                                                           self.entropy_diagonal_lines,
                                                                           self.laminarity,
                                                                           self.trapping_time,
                                                                           self.longest_vertical_line,
                                                                           self.entropy_vertical_lines,
                                                                           self.average_white_vertical_line,
                                                                           self.longest_white_vertical_line,
                                                                           self.longest_white_vertical_line_inverse,
                                                                           self.entropy_white_vertical_lines,
                                                                           self.ratio_determinism_recurrence_rate,
                                                                           self.ratio_laminarity_determinism)
