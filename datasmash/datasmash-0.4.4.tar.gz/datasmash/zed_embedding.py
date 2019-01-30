import os
import subprocess as sp
import numpy as np
from typing import Dict
from datasmash.utils import (quantizer, D3MDatasetLoader, pprint_dict,
                             matrix_list_p_norm, smash)
from datasmash.config import BIN_PATH
from datasmash._version import __version__
from sklearn.manifold import MDS


class zSmashEmbedding():
    """

    """
    def __init__(self, *, embedder=None):
        assert os.path.isfile(os.path.join(BIN_PATH, 'smash')), "Error: invalid bin path."
        self._bin_path = os.path.abspath(os.path.join(BIN_PATH, 'smash'))
        self._cwd = os.getcwd()
        self._d3m_reader = D3MDatasetLoader()
        self._tmp_dir = ''
        self._channel_dirs = []
        self._channel_partition_map = {}
        self._selected_channels = set()
        self._num_streams = 0
        if embedder is not None:
            self._embed_class = embedder
        else:
            self._embed_class = MDS(n_components=2, dissimilarity='precomputed')

        self._channels = None

    def _fit_one_channel(self, directory):
        """

        """
        _, _, _, partition = quantizer(directory,
                                       inplace=True,
                                       use_genesess=False,
                                       problem_type='unsupervised',
                                       num_streams=self._num_streams)
        return partition

    def fit_transform(self, X):
        """

        """
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='train')
        self._tmp_dir, self._channel_dirs, self._num_streams = self._d3m_reader.write_libs(problem_type='unsupervised')

        channels = self._channels
        if channels is not None:
            if channels == -1:
                pass
            elif not isinstance(channels, list):
                channels = [channels]
            selected_channels = ['channel_' + str(c) for c in channels]
            self._selected_channels = set(selected_channels)
        elif bool(self._selected_channels):
            selected_channels = self._selected_channels
        else:
            selected_channels = self._channel_dirs

        for channel_dir in selected_channels:
            partition = self._fit_one_channel(channel_dir)
            channel_name = channel_dir.split('/')[-1]
            self._channel_partition_map[channel_name] = partition

        #if verbose:
        print('Chosen partition:')
        pprint_dict(self._channel_partition_map)

        # run smash to get the distance matrix

        distance_matrices = []
        for channel_dir, partition in self._channel_partition_map.items():
            channel_path = os.path.join(self._tmp_dir, channel_dir)
            input_data = os.path.join(channel_path, 'dataset')
            output_file = os.path.join(channel_path, 'H.dst')
            results = smash(input_data, outfile=output_file)
            distance_matrices.append(results)

        final_dist_matrix = matrix_list_p_norm(distance_matrices, p=2)
        feature_vector = self._embed_class.fit_transform(results)

