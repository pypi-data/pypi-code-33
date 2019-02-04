# -*- coding: utf-8 -*-

"""
A collection of ISamples, with tools to iterate and organize.
"""

import json
import random
from abc import abstractmethod
from typing import List, Dict, Union

from raid.data.interface.i_sample import ISample
from raid.data.functional.resampler import oversample, undersample
from raid.data.functional.stratifier import stratify_samples_weighted
from raid.visual.plotter import Plotter

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class DatasetException(Exception):
    pass


class IDataset:

    def __init__(self, samples: List[ISample]=None, label_map: Dict[int, str] = None):
        self.samples = samples
        self.label_map: dict = label_map

    # ===================================================================================================
    # Functions to overload.
    # ===================================================================================================

    @staticmethod
    @abstractmethod
    def create_dataset(samples: List[ISample], label_map: Dict[int, str]):
        """ An overridable function to create a dataset of this type. """
        return IDataset(samples, label_map)

    # ===================================================================================================
    # Sampling and Balancing Functions
    # ===================================================================================================

    def stratify_k_fold(self, k: int = 2) -> List['IDataset']:
        """ Split the data into equally distributed folds. """
        return self.stratify_weighted([1 for _ in range(k)])

    def stratify_weighted(self, weights: List[float]) -> List['IDataset']:
        """ Split the data into balanced sets with the given weights. """

        # We need at least 2 folds.
        assert len(weights) >= 2

        samples_list = stratify_samples_weighted(self.samples, weights)
        datasets = [self.create_dataset(s, self.label_map) for s in samples_list]
        return datasets

    def create_oversampled(self, ratio: float=1.0) -> 'IDataset':
        """ Creates a data-set with re-sampled elements to even out the distribution.
        Will duplicate the number of least elements to at least the ratio of the max elements.
        """
        samples = oversample(self.samples, ratio)
        return self.create_dataset(samples, self.label_map)

    def create_undersampled(self, ratio: float=1.0):
        """ Creates a data-set with re-sampled elements to even out the distribution.
        Will remove the number of max elements to have at most the ratio of the delta with the min elements.
        """
        samples = undersample(self.samples, ratio)
        return self.create_dataset(samples, self.label_map)

    def shuffle(self, seed: int=None, balanced: bool=True):
        """ Shuffle our sample data. """
        if seed is not None:
            random.seed(seed)

        if balanced:
            self.samples = self._balanced_shuffle(seed)
        else:
            random.shuffle(self.samples)

    def _balanced_shuffle(self, seed: int=None):
        """ Shuffle the data whilst trying to maintain an even distribution of the data. """
        if seed is not None:
            random.seed(seed)

        distribution = self.get_label_distribution_index()
        items = list(distribution.items())
        items.sort(key=lambda x: x[1])

        sample_pool = self.samples[:]
        sample_bins = {}

        for k, v in items:
            sample_bin = sample_bins[k] = []
            for i in range(len(sample_pool) - 1, -1, -1):
                if k in sample_pool[i].labels:
                    sample_bin.append(sample_pool[i])
                    sample_pool.pop(i)

        n_bins = min([v for _, v in items])
        batch_bins = [[] for _ in range(n_bins)]

        for i in range(n_bins):
            batch_bin = batch_bins[i]
            for k, samples in sample_bins.items():
                # How many samples to put in this bin?
                n_bin_stride = int(len(samples) / n_bins)
                start_index = i * n_bin_stride
                end_index = (i + 1) * n_bin_stride

                # Take the next round of samples. In the last round, we add everything remaining.
                batch_samples = samples[start_index:end_index] \
                    if i != (n_bins - 1) \
                    else samples[start_index:]

                # Concat the new samples into the batch bin.
                batch_bin += batch_samples

        # Finally, shuffle each batch internally and then concatenate them.
        final_samples = []
        for batch in batch_bins:
            random.shuffle(batch)
            final_samples += batch

        return final_samples

    def get_batch(self, index: int, batch_size: int) -> List[ISample]:
        """ Returns a batch of samples for this index and batch size. """
        start_index = index * batch_size
        end_index = start_index + batch_size
        if end_index > len(self.samples):
            raise DatasetException(f"Cannot fetch batch {index}x{batch_size}: Index exceeded!")
        return self.samples[start_index:end_index]

    def get_batch_count(self, batch_size: int):
        """ How many batches would we get if we used this batch size? """
        if self.count < batch_size:
            raise DatasetException(f"Your batch size {batch_size} is bigger than your entire dataset ({self.count}).")
        return self.count // batch_size

    # ===================================================================================================
    # Label Mapping.
    # ===================================================================================================

    def get_semantic_label(self, label_index: int) -> str:
        """ Get the semantic label for the index. """
        return self.label_map[label_index]

    # ===================================================================================================
    # Visualization and Exploration.
    # ===================================================================================================

    def get_label_distribution_index(self) -> Dict[int, int]:
        """ Returns a dictionary mapping, from a string label to the number of instances. """
        distribution_map = {}

        for sample in self.samples:
            for i_label in sample.labels:
                if i_label not in distribution_map:
                    distribution_map[i_label] = 0
                distribution_map[i_label] += 1

        return distribution_map

    def get_label_distribution_semantic(self) -> Dict[str, int]:
        """ Returns a dictionary mapping, from a string label to the number of instances. """
        index_map = self.get_label_distribution_index()
        distribution_map = {self.get_semantic_label(k): v for (k, v) in index_map.items()}
        return distribution_map

    def draw_label_distribution(self, path: str, n_max: int=-1, color_scheme: str=None):
        Plotter.save_distribution_map(path, self.get_label_distribution_semantic(), n_max, color_scheme)

    def export_label_distribution_semantic(self, path: str):
        data = self.get_label_distribution_semantic()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def export_label_distribution_index(self, path: str):
        data = self.get_label_distribution_index()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def get_samples(self, labels: Union[int, List[int]], max_samples: int=0):
        """ Get a list of samples for the label. """

        samples = []

        # Cast to list if user gave me an int.
        if type(labels) is int:
            labels = [labels]

        label_set = set(labels)
        for sample in self.samples:
            sample_set = set(sample.labels)

            # Check if it contains the label.
            valid = not label_set.isdisjoint(sample_set)
            if valid:
                samples.append(sample)
                if 0 < max_samples <= len(samples):
                    break
        return samples

    # ===================================================================================================
    # Properties.
    # ===================================================================================================

    def __len__(self):
        return self.count

    @property
    def count(self):
        return len(self.samples)

    def count_label(self, label: int):
        """ Count the number of times this label appears. """
        return self.count_labels([label])

    def count_labels(self, labels: List[int]):
        """ Count the number of times any of these labels appear. """
        return sum([1 for s in self.samples if len(set(s.labels).intersection(set(labels))) > 0])

    # ===================================================================================================
    # Housekeeping Stuff.
    # ===================================================================================================

    def __str__(self):
        return f"[Dataset {len(self.samples)} Samples: {self.get_label_distribution_semantic()}]"
