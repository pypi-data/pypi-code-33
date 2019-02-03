# -*- coding: utf-8 -*-

"""
Functions to re-sample the dataset either by adding or removing elements.
The aim is to even out the label distribution.
"""

from typing import List
from k_util.logger import Logger
from raid.data.interface.i_sample import ISample
from raid.data.functional.sample_distribution import get_label_distribution

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


def oversample(samples: List[ISample], ratio: float=1.0):
    """ Creates a data-set with re-sampled elements to even out the distribution.
        Will duplicate the number of least elements to at least the ratio of the max elements.
    """
    assert (0.0 <= ratio <= 1.0)

    # Make a copy of the data. We are adding to this.
    new_samples = samples[:]

    # Get the distribution.
    distribution_list = get_label_distribution(samples)
    Logger.field("Old Distribution (10 Max)", distribution_list[:min(10, len(distribution_list))])

    # Find m, the minimum number each label must represent.
    m = int(max([d.count for d in distribution_list]) * ratio)
    Logger.field("Oversampling M Value", m)

    # Order the distribution by lowest to highest.
    distribution_list.sort(key=lambda x: x.count)

    # For each label in the distribution, find the deficit amount n.
    for distribution in distribution_list:
        current_count = sum([1 for s in new_samples if distribution.label in s.labels])
        n = max(0, m - current_count)
        if n == 0:
            continue

        # Add them sweet samples.
        i = 0
        while n > 0:
            n -= 1
            new_samples.append(distribution.samples[i])

            # Loop the index.
            i += 1
            if i >= len(distribution.samples):
                i = 0

    distribution_list = get_label_distribution(new_samples)
    Logger.field("Oversampling Size Delta", f"{len(samples)} -> {len(new_samples)}")
    Logger.field("New Distribution (10 Max)", distribution_list[:min(10, len(distribution_list))])
    return new_samples


def undersample(samples: List[ISample], ratio: float=1.0):
    """ Creates a data-set with re-sampled elements to even out the distribution.
        Will remove the number of max elements to have at most the ratio of the delta with the min elements.
    """
    assert(0.0 <= ratio <= 1.0)

    # Make a copy of the data. We are adding to this.
    new_samples = samples[:]

    # Get the distribution.
    distribution_list = get_label_distribution(samples)
    Logger.field("Old Distribution (10 Max)", distribution_list[:min(10, len(distribution_list))])

    # Find m, the maximum number each label must represent.
    count_list = [d.count for d in distribution_list]
    min_count = min(count_list)
    max_count = max(count_list)
    delta = max_count - min_count
    m = int(min_count + delta * ratio)
    Logger.field("Undersample M Value", m)

    # Order the distribution by highest to lowest.
    distribution_list.sort(key=lambda x: x.count, reverse=True)

    # For each label in the distribution, find the deficit amount n.
    for distribution in distribution_list:
        current_count = sum([1 for s in new_samples if distribution.label in s.labels])
        n = max(0, current_count - m)  # This is how many we need to remove.
        if n == 0:
            continue

        # Remove them sweet samples.
        i = 0
        while n > 0:
            n -= 1
            new_samples.remove(distribution.samples[i])

            # Loop the index.
            i += 1

    distribution_list = get_label_distribution(new_samples)
    Logger.field("Undersampling Size Delta", f"{len(samples)} -> {len(new_samples)}")
    Logger.field("New Distribution (10 Max)", distribution_list[:min(10, len(distribution_list))])
    return new_samples
