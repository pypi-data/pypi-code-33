from ..utils import calc_num_batch, rescale_img, take, path_listdir
import numpy as np
import tensorflow as tf
from abc import ABCMeta, abstractmethod
import os
to_categorical = tf.keras.utils.to_categorical


class IndexIter:
    def __init__(self, num_data, batch_size, use_uniform=False, shuffled=True):
        self.i = 0
        self.num_data = num_data
        self.num_batch = calc_num_batch(num_data, batch_size)
        self.batch_size = batch_size
        self.use_uniform = use_uniform
        self.shuffled = shuffled
        if not use_uniform:
            if shuffled:
                self.indexes = np.random.permutation(self.num_data)
            else:
                self.indexes = np.arange(self.num_data)

    def __len__(self):
        return self.num_batch

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.num_data:
            raise StopIteration

        if not self.use_uniform:
            inds = self.indexes[self.i: self.i + self.batch_size]

        else:
            if self.shuffled:
                inds = np.random.choice(self.num_data, size=self.batch_size)
            else:
                inds = np.arange(self.i, min(self.i + self.batch_size, self.num_data))

        self.i += len(inds)
        return inds


class DataIter(metaclass=ABCMeta):
    def __init__(self, num_data, batch_size, use_uniform=False, shuffled=True):
        self.index_iterator = IndexIter(num_data, batch_size, use_uniform, shuffled=shuffled)

    def __len__(self):
        return len(self.index_iterator)

    def __iter__(self):
        return self

    def __next__(self):
        Is = next(self.index_iterator)
        return self.fetch_data(Is)

    @abstractmethod
    def fetch_data(self, Is):
        return NotImplemented


class MappedDataIter(metaclass=ABCMeta):
    def __init__(self, data_iter, f):
        self.data_iter = data_iter
        self.f = f

    def __len__(self):
        return len(self.data_iter)

    def __iter__(self):
        return self

    def __next__(self):
        d = next(self.data_iter)
        return self.f(d)


class FileIter(DataIter, metaclass=ABCMeta):
    def __init__(self, root_folder, batch_size, shuffled=True):
        self.root_folder = root_folder
        self.fpaths = path_listdir(root_folder, only_files=True)
        num_data = len(self.fpaths)

        super().__init__(num_data, batch_size, shuffled=shuffled)

    def fetch_data(self, Is):
        fpaths = take(self.fpaths, Is)
        Xs = list(map(self.load_data_one, fpaths))
        return Is, Xs

    @abstractmethod
    def load_data_one(self, fpath):
        return NotImplemented


class PatchXYIter(DataIter, metaclass=ABCMeta):
    def __init__(self, num_image, k, batch_size, shape, use_uniform=False):
        H, W = shape[:2]
        Hp, Wp = H - k + 1, W - k + 1
        num_data = self.calculate_N(num_image, H, W, k)

        super().__init__(num_data, batch_size, use_uniform=use_uniform)
        self.k = k
        self.shape = shape
        self.patch_points = Hp, Wp
        self.num_image = num_image
        self.c = 1 if len(shape) == 2 else shape[2]

    @staticmethod
    def calculate_N(num_image, H, W, K):
        Hp, Wp = H - K + 1, W - K + 1
        return num_image * Hp * Wp

    def unravel_inds(self, inds):  # [i_img, i, j]
        return np.unravel_index(inds, (self.num_image,) + self.patch_points)

    # from here

    def process_data(self, Is, Xs):
        XPatchs = self.images_to_patches(Is, Xs)
        Ys = self.patches_to_label(XPatchs)  # [N, W, W, C, 256]
        XPatchs[:, self.k: 2 * self.k, self.k: 2 * self.k] = 0  # [N, PW, PH, C]
        XPatchs = rescale_img(XPatchs, 0, 255, 0., 1.)
        return Is, (XPatchs, Ys)

    def images_to_patches(self, Is, Xs):
        N = len(Is)
        PW, PH = 3 * self.k, 3 * self.k
        patches_shape = (N, PW, PH, self.c)
        patches = np.empty(patches_shape, dtype=Xs.dtype)
        for i, (_, x, y) in enumerate(zip(*self.unravel_inds(Is))):
            patches[i, ...] = Xs[i, x: x + PW, y: y + PH]
        return patches

    def patches_to_label(self, patches):
        patch_center = patches[:, self.k: 2 * self.k, self.k: 2 * self.k].copy()
        N, W, _, C = patch_center.shape
        resultsss = list()
        for i in range(W):
            resultss = list()
            for j in range(W):
                results = list()
                for c in range(C):
                    i_j_c = to_categorical(patch_center[:, i, j, c], 256)  # [N, 256]
                    results.append(i_j_c)
                resultss.append(results)
            resultsss.append(resultss)

        y_batch = np.array(resultsss)  # [W, W, C, N, 256]
        return np.rollaxis(y_batch, 3, 0)  # [N, W, W, C, 256]
