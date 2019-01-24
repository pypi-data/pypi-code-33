import os
import collections

from tensorop import transforms as tfms
from tqdm import tqdm
import nmpy as np

from torch.utils.data import Dataset
import torch
from PIL import Image

class DatasetManager(x):
    def __init__(self,dataset,transform=None):
        self.dataset = dataset
        self.transform = transform
        self._transform_state = None

    def __enter__(self):
        if self.transform:
            self._transform_state = self.dataset.transform
            self.dataset.transform = self._transform_state
        return self.dataset

    def __exit__(self,*args):
        if self._transform_state:
            self.dataset.transform = self._transform_state
            
class BatchSplit(x):
    def __init__(self,batch):
        self.batch=batch
    
    def __iter__(self):
        batch_len = len(self.batch["input"])
        for i in range(batch_len):
            single_sample = {k: v[i] for k,v in self.batch.items()}
            single_sample['index'] = i
            yield single_sample
        raise StopIteration

