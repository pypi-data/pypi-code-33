#!/usr/bin/env python

import torch as th
from torch.utils.data import Dataset

from functools import reduce

from PIL import ImageFile


ImageFile.LOAD_TRUNCATED_IMAGES = True


def flatten(tensor_list):
    return th.cat([t.view(1, -1) for t in tensor_list])


def unflatten(tensor, tensor_list):
    output = []
    start = 0
    for t in tensor_list:
        num = reduce(t.size(), lambda x, y: x * y)
        output.append(tensor[start:start + num].view(t.size()))
        start += num
    return output


def split_dataset(dataset, num_samples=None):
    assert isinstance(num_samples, (list, tuple))
    permutation = th.randperm(len(dataset))
    datasets = []
    offset = 0
    for size in num_samples:
        indices = permutation[offset:offset + size]
        datasets.append(IndexDataset(dataset, indices))
        offset += size
    return datasets


class IndexDataset(Dataset):
    def __init__(self, dataset, indices):
        self.dataset = dataset
        self.indices = indices

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        return self.dataset[self.indices[index]]


class NoOptScheduler(object):
    def __init__(self):
        pass

    def step(*args, **kwargs):
        pass
