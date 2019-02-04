# -*- coding: utf-8 -*-

"""
Functions to stratify and split data while maintaining balance.
We don't know if the data is single label or multi label.
"""

from typing import List, Set
from raid.data.interface.i_sample import ISample
from raid.data.functional.sample_distribution import get_label_distribution

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


def stratify_samples_weighted(samples: List[ISample], weights: List[float]) -> List[List[ISample]]:
    """ Split the list of samples into sets of data according to the weight distribution. """

    # Create the original sample distribution.
    distribution_list = get_label_distribution(samples)
    distribution_list.sort(key=lambda x: x.count)

    # The output.
    final_samples_list: List[List[ISample]] = [[] for _ in range(len(weights))]

    # Create the folds.
    consumed_map: Set[str] = set()  # Store a map of all the samples we used to not duplicate them.

    # Start from the smallest, and fan them out to our sample list.
    for distribution in distribution_list:
        sample_list = _distribute_samples(distribution.samples, consumed_map, weights)
        for i in range(len(weights)):
            final_samples_list[i] += sample_list[i]

    return final_samples_list


# ===================================================================================================
# Supporting Functions.
# ===================================================================================================


def _distribute_samples(
        samples: List[ISample],
        consumed_map: Set[str],
        weights: List[float]) -> List[List[ISample]]:
    """ Given a list of samples, a map of used samples, and weights, distribute these into an even split. """

    # Remove any duplicated samples.
    samples = [s for s in samples if s.id not in consumed_map]

    # Calculate the concrete sample distribution.
    n_samples: int = len(samples)
    k: int = len(weights)
    count_divider = sum(weights)
    distribution = [int((w * n_samples) / count_divider) for w in weights]

    # The remaining samples go into the last bin.
    distribution[-1] = n_samples - sum(distribution[:k - 1])

    # Create the sample list.
    samples_list = [[] for _ in range(k)]
    start_index = 0
    for i in range(k):
        end_index = start_index + distribution[i]
        samples_list[i] = samples[start_index:end_index]
        start_index = end_index

    # Add all samples to the map so it doesn't get appended twice.
    for s in samples:
        consumed_map.add(s.id)

    return samples_list
