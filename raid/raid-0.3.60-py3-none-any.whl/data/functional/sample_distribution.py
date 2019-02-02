# -*- coding: utf-8 -*-

"""
Tools to help understand the distribution of the sample labels.
"""

from typing import List
from raid.data.interface.i_sample import ISample

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class _SampleDistribution:
    def __init__(self, label: int):
        """ Stores information about how a sample is distributed in the dataset. """
        self.samples: List[ISample] = []
        self.label: int = label
        self.count: int = 0

    def __repr__(self):
        return f"{self.label}: {self.count}"


def get_label_distribution(samples: List[ISample]) -> List[_SampleDistribution]:

    distribution_map = {}

    for sample in samples:
        for label in sample.labels:
            if label not in distribution_map:
                distribution_map[label] = _SampleDistribution(label)

            # Edit the record.
            distribution = distribution_map[label]
            distribution.samples.append(sample)
            distribution.count += 1

    return list(distribution_map.values())
