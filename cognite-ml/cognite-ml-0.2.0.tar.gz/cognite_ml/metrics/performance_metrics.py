#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import pandas as pd
from cognite._utils import granularity_to_ms

__all__ = ["RangeBasedPrecisionRecall"]


class RangeBasedPrecisionRecall:
    """Class for Precision and Recall for Range-Based Anomaly Detection

    :param anomaly_labels: list of timestamp tuples of actual anomaly labels with (start_time, end_time)
    :param predicted_labels: list of timestamp tuples of predicted anomaly labels with (start_time, end_time)
    :param alpha: relative weight of existence reward
    :param beta: relative weight of overlap reward
    :param bias_type: positional bias type ('front', 'flat', 'tail')
    :param granularity: granularity of tieme series data used to generate the predicted anomaly labels

    Lee et al. 2018
    https://arxiv.org/pdf/1801.03175.pdf
    """

    def __init__(self, anomaly_labels, predicted_labels, alpha=0.5, beta=0.5, bias_type=None, granularity=None):

        self.anomaly_labels = anomaly_labels
        self.predicted_labels = predicted_labels
        self.alpha = alpha
        self.beta = beta
        self.bias_type = bias_type
        self.granularity = granularity
        self.precision = None
        self.recall = None

    def __is_contained(self, a_range, b_range):
        """returns whether a_range is contained in b_range where range is given by a tuple of (start, end) timestamps"""
        if a_range[0] >= b_range[0] and a_range[1] <= b_range[1]:
            return True
        else:
            return False

    def __is_empty(self, any_structure):
        """returns whether a data structure is empty or not"""
        if any_structure:
            return False
        else:
            return True

    def __get_intersection(self, a_range, b_range):
        """returns the union of two ranges a and b where each range is given by a tuple of (start, end) timestamps"""
        a_left, a_right = a_range
        b_left, b_right = b_range
        end_pts = sorted([a_left, a_right, b_left, b_right])
        middle = [end_pts[1], end_pts[2]]
        if a_right >= b_left and b_right >= a_left:
            intersection = middle
        else:
            intersection = []

        return tuple(intersection)

    def __get_length(self, a_range):
        """returns the length of a range a given by a tuple of (start, end)"""
        length = a_range[1] - a_range[0]  # measured in 'ms'

        if self.granularity is not None:
            granularity_in_ms = granularity_to_ms(self.granularity)
            length = length / granularity_in_ms

        return length

    def __get_step_ranges(self, a_range):
        """returns a list of timestamps that span the range given by a tuple of (start, end) times"""
        if self.granularity is not None:
            step = granularity_to_ms(self.granularity)
        else:
            step = 1

        points = list(range(a_range[0], a_range[1] + step, step))

        return [(points[i], points[i + 1]) for i in range(len(points) - 1)]

    def __positional_bias(self, position, range_length):
        """returns positional bias based on type"""
        if self.bias_type == "front":
            return range_length - position + 1
        elif self.bias_type == "tail":
            return position
        else:
            return 1

    def __overlap_size(self, a_range, b_range):
        """returns the relative overlap size of a_range wrt a_range \intersect b_range"""
        my_value = 0
        max_value = 0
        step_ranges = self.__get_step_ranges(a_range)
        intersection = self.__get_intersection(a_range, b_range)
        range_length = len(step_ranges)

        if self.__is_empty(intersection) or range_length == 0:
            return 0.0
        else:
            for i in range(range_length):
                bias = self.__positional_bias(i, range_length)
                max_value = max_value + bias
                step_range = step_ranges[i]
                if self.__is_contained(step_range, intersection):
                    my_value = my_value + bias

            return my_value / max_value

    def __cardinality_factor(self, a_range, list_range):
        """returns a factor that is inversely proportional to the cardinality of anomaly_range.
        Takes the value 1 if anomaly_range overlaps with at most one predicted range in predicted_labels"""
        overlaps = []
        for b_range in list_range:
            overlap = self.__get_intersection(a_range, b_range)
            if not self.__is_empty(overlap):
                overlaps.append(overlap)

        if len(overlaps) >= 1:
            return 1 / len(overlaps)
        else:
            return 0.0

    def __overlap_reward(self, anomaly_range, predicted_labels):
        """returns the overlap reward based on size, position and cardinality
        of one anomaly range wrt all predicted anomaly labels"""

        return self.__cardinality_factor(anomaly_range, predicted_labels) * sum(
            [self.__overlap_size(anomaly_range, predicted_range) for predicted_range in predicted_labels]
        )

    def __existence_reward(self, a_range, list_range):
        """returns the existence reward of one anomaly_range wrt all predicted anomaly labels"""

        overlaps = []
        for b_range in list_range:
            overlap = self.__get_intersection(a_range, b_range)
            if not self.__is_empty(overlap):
                overlaps.append(overlap)

        if len(overlaps) >= 1:
            return 1
        else:
            return 0.0

    def __recall_of_one_range(self, anomaly_range, predicted_labels):
        """returns recall score of one anomaly range wrt all predicted anomaly labels"""
        return self.alpha * self.__existence_reward(
            anomaly_range, predicted_labels
        ) + self.beta * self.__overlap_reward(anomaly_range, predicted_labels)

    def __precision_of_one_range(self, prediction_range, anomaly_labels):
        """returns the precision based on size, position and cardinality
        of one predicted anomaly range wrt all anomaly labels"""

        return self.__cardinality_factor(prediction_range, anomaly_labels) * sum(
            [self.__overlap_size(prediction_range, anomaly_range) for anomaly_range in anomaly_labels]
        )

    def get_recall(self):
        """returns recall score of all anomaly labels wrt all predicted anomaly labels"""
        vals = [
            self.__recall_of_one_range(anomaly_range, self.predicted_labels) for anomaly_range in self.anomaly_labels
        ]

        self.recall = sum(vals) / len(vals)

        return self.recall

    def get_precision(self):
        """returns precision score of all anomaly labels wrt all predicted anomaly labels"""
        vals = [
            self.__precision_of_one_range(prediction_range, self.anomaly_labels)
            for prediction_range in self.predicted_labels
        ]

        self.precision = sum(vals) / len(vals)

        return self.precision

    def get_detection_lags(self):
        """returns the detection lag of first flagged anomaly range on or after each anomaly start"""
        detect_lags = []
        anom_lengths = []

        for i in range(len(self.anomaly_labels)):
            an_win = self.anomaly_labels[i]
            next_an_start = self.anomaly_labels[i + 1][0] if i < len(self.anomaly_labels) - 1 else math.inf
            try:
                first_detect = sorted(
                    [pr_win[0] for pr_win in self.predicted_labels if an_win[0] <= pr_win[0] < next_an_start]
                )[0]
                detect_lags.append(pd.to_datetime(first_detect, unit="ms") - pd.to_datetime(an_win[0], unit="ms"))
            except IndexError:
                detect_lags.append("Not detected")
            anom_lengths.append(pd.to_datetime(an_win[1], unit="ms") - pd.to_datetime(an_win[0], unit="ms"))

        return detect_lags, anom_lengths

    def print_test_performance(self):
        """ returns nothing: prints summary of algorithm performance on test case"""
        print("Range-based Precision:", round(100 * self.get_precision(), 2), "%")
        print("Range-based    Recall:", round(100 * self.get_recall(), 2), "%")
        anomaly_detection_lags, anomaly_window_lengths = self.get_detection_lags()
        print("Delay(s) before first detection of anomaly:")
        for i in range(len(anomaly_detection_lags)):
            if anomaly_detection_lags[i] == "Not detected":
                print("  #{}: Not detected".format(i + 1))
            else:
                print("  #{}: {} into window of {}".format(i + 1, anomaly_detection_lags[i], anomaly_window_lengths[i]))
