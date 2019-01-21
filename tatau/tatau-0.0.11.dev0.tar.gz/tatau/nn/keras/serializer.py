import os

import numpy as np

from tatau.nn.tatau import serializer


class WeightsSerializer(serializer.WeightsSerializer):
    @classmethod
    def save(cls, weights, path):
        path_npz = '{}.npz'.format(path)
        np.savez_compressed(path_npz, *weights)
        os.rename(path_npz, path)

    @classmethod
    def load(cls, path):
        weights_file = np.load(path)
        return [weights_file[r] for r in weights_file.files]

    @classmethod
    def to_numpy(cls, weights):
        return weights

