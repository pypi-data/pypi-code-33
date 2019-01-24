import numpy as np
from scipy.misc import imread
from .iterator import DataIter, PatchXYIter, FileIter
from ..utils import take


class MemoryXYIter(DataIter):
    def __init__(self, x, y, batch_size):
        super().__init__(len(x), batch_size)
        assert len(x) == len(y)

        self.x = x
        self.y = y

    def fetch_data(self, Is):
        return self.x[Is], self.y[Is]


class MemoryPatchXYIter(PatchXYIter):
    def __init__(self, x, k, batch_size, shape):
        num_image = len(x)
        super().__init__(num_image, k, batch_size, shape)
        self.x = x

    def fetch_data(self, Is):
        i_img = self.unravel_inds(Is)[0]
        Xs = self.x[i_img]
        Is, XYs = self.process_data(Is, Xs)
        return XYs


class ImagefileXIter(FileIter):
    def fetch_data(self, Is):
        Is, Xs = super().fetch_data(Is)
        Xs = np.array(Xs)
        return Is, Xs

    def load_data_one(self, fpath):
        return imread(fpath)
