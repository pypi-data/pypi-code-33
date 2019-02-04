# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

import os
import uuid
from typing import Union, List, Dict

from raid.data.concrete.image_single_clf_sample import ImageSingleClfSample
from raid.data.interface.i_dataset import IDataset
from raid.data.interface.i_sample import ISample

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class ImageSingleClfDataset(IDataset):

    def __init__(self, samples: List[ISample]=None, label_map: Dict[int, str] = None):
        super().__init__(samples, label_map)

    @staticmethod
    def create_dataset(samples: List[ISample], label_map: Dict[int, str]):
        return ImageSingleClfDataset(samples, label_map)

    @classmethod
    def create_from_directory(cls, path: str):
        """ Create a dataset. """

        folders = os.listdir(path)
        label_map_index, label_map_item = cls.create_label_maps(folders)
        samples: List[ISample] = []

        for folder in folders:
            folder_path = os.path.join(path, folder)
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                label = label_map_item[folder]
                sample = cls.create_sample_from_image_path(file_path, label, label_map_index)
                samples.append(sample)

        dataset = IDataset(samples)
        dataset.label_map = label_map_index
        dataset.label_map_item = label_map_item
        return dataset

    @staticmethod
    def create_label_maps(labels: List[str]) -> (dict, dict):
        """ Given a list of elements, create a one-to-one mapping of indices. """
        label_index_to_string = {}
        label_string_to_index = {}
        item_set = set(labels)

        for i, item in enumerate(item_set):
            label_index_to_string[i] = item
            label_string_to_index[item] = i

        return label_index_to_string, label_string_to_index

    @staticmethod
    def create_sample_from_image_path(image_path: str, label: int, label_map: Dict[int, str]):
        sample = ImageSingleClfSample(
            uuid.uuid4().hex,
            image_path,
            label,
            label_map
        )
        return sample
