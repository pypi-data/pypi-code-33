import os
import subprocess as sp
import numpy as np
import json
from typing import Dict
from datasmash.utils import pprint_dict, matrix_list_p_norm, smash
from datasmash.d3m_dataset_loader import D3MDatasetLoader
from datasmash.quantizer import Quantizer, fit_one_channel
from datasmash.config import BIN_PATH
from datasmash._version import __version__

from d3m.metadata import hyperparams, params, base
from d3m.container import dataset, numpy
from d3m.primitive_interfaces.base import CallResult, DockerContainer
from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase


Inputs = dataset.Dataset
Outputs = numpy.matrix


class Params(params.Params):
    """
    a no-op
    """
    pass


class Hyperparams(hyperparams.Hyperparams):
    """
    a no-op
    """
    quantizer_core_hours = hyperparams.Bounded(
        default = 28,
        lower = 1,
        upper = None,
        description = ('Number of core-hours one wishes to allot to the'
                       + ' QUANTIZATION PORTION of the algorithm.'),
        semantic_types = ['https://metadata.datadrivendiscovery.org/types/TuningParameter',
                          'https://metadata.datadrivendiscovery.org/types/ResourcesUseParameter']
    )


class d3m_SmashDistanceMetricLearning(TransformerPrimitiveBase[Inputs, Outputs,
                                                           Hyperparams]):
    """

    """
    __author__ = "UChicago"
    metadata = base.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.d3m_SmashDistanceMetricLearning",
        "primitive_family": "DATA_TRANSFORMATION",
        "python_path": "d3m.primitives.datasmash.d3m_SmashDistanceMetricLearning",
        "source": {
        	'name': 'UChicago',
			'contact': 'mailto:virotaru@uchicago.edu'
		},
        "version": __version__,
        "id": "40cbbab4-1415-404e-9935-f1a56c1ece10",
        'installation': [
            {'type': base.PrimitiveInstallationType.PIP,
             'package': 'datasmash',
             'version': __version__
            }
        ],
        "keywords": [
            'time',
            'series',
            'data smashing',
            'data-smashing',
            'data_smashing',
            'datasmashing',
            'distance matrix',
            'distance metric',
            'parameter-free',
            'hyperparameter-free'
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed)


        assert os.path.isfile(os.path.join(BIN_PATH, 'smash')), "Error: invalid bin path."

        self._bin_path = os.path.abspath(os.path.join(BIN_PATH, 'smash'))
        self._cwd = os.getcwd()
        self._d3m_reader = D3MDatasetLoader()
        self._tmp_dir = ''
        self._channel_dirs = []
        self._num_streams = 0
        self._partition = None
        self._selected_channels = set()
        self._channel_parameter_map = {}
        self._channels = None

        self._quantizer_core_hours = self.hyperparams['quantizer_core_hours']

    #def _fit_one_channel(self, directory):
    #    """

    #    """
    #    #_, _, _, partition = quantizer(directory,
    #    #                               inplace=True,
    #    #                               use_genesess=False,
    #    #                               problem_type='unsupervised',
    #    #                               num_streams=self._num_streams)
    #    #return partition
    #    qtz = Quantizer(problem_type='unsupervised', multi_partition=False)
    #    X = qtz.fit_transform(directory, output_type='filename')
    #    return X, qtz

    def produce(self, *, inputs: Inputs, timeout: float = None,
                iterations: int = None) -> CallResult[Outputs]:
        """

        """
        print('Datasmash version:',__version__)
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
            X, qtz = fit_one_channel(channel_dir, problem_type='unsupervised',
                                     num_quantizations=1,
                                     #multi_partition=False,
                                     core_hours=self._quantizer_core_hours)
            channel_name = os.path.basename(channel_dir)
            self._channel_parameter_map[channel_name] = (X, qtz)

        #if verbose:
        #print('Chosen partition:')
        #pprint_dict(self._channel_parameter_map)

        # run smash to get the distance matrix

        distance_matrices = []
        for channel_dir, (X, _) in self._channel_parameter_map.items():
            channel_path = os.path.join(self._tmp_dir, channel_dir)
            #input_data = os.path.join(channel_path, 'dataset')
            #X.to_csv(input_data, sep=' ', header=False, index=False)
            output_file = os.path.join(channel_path, 'H.dst')
            results = smash(X[0], outfile=output_file)
            distance_matrices.append(results)

        final_dist_matrix = matrix_list_p_norm(distance_matrices, p=2)
        return CallResult(final_dist_matrix)
