import os
import time
import numpy as np
import pandas as pd
from datasmash.quantizer import Quantizer, mkqdir, vectorize_label
from datasmash.utils import smashmatch, pprint_dict, argmax_prod_matrix_list
from datasmash.config import CWD, BIN_PATH


class SmashBase(object):
    """

    """
    def __init__(self, *, classifier, **quantizer_hyperparams):
        smashmatch_path = os.path.join(BIN_PATH, 'smashmatch')
        assert os.path.isfile(smashmatch_path), "invalid bin path."
        self._tmp_dir = ''
        self._classifier = classifier
        self._quantizer = Quantizer(**quantizer_hyperparams)
                                    problem_type='supervised',
                                    multi_partition=multi_partition)
        self._fitted = False

    @property
    def classifier(self):
        return self._classifier

    @classifier.setter
    def classifier(self, classifier):
        self._fitted = False
        self._classifier = classifier

    @property
    def quantizer(self):
        return self._quantizer

    @quantizer.setter
    def quantizer(self, **quantizer_hyperparams):
        return 






    def fit(self, X, y):
        """

        """
        self._tmp_dir = mkqdir(X, labels=y, parent_dir='./')
        y_ = vectorize_label(X, y)
        X_ = self.quantizer.fit_transform(self._tmp_dir)

    def predict(self, X):
        """

        """


import time
import os
import subprocess as sp
import numpy as np
import pandas as pd
from typing import Dict
from sklearn.cluster import KMeans
from datasmash.utils import smash, smashmatch
from datasmash.d3m_dataset_loader import D3MDatasetLoader
from datasmash.quantizer import Quantizer
from datasmash.utils import pprint_dict, argmax_prod_matrix_list
from datasmash.config import CWD, BIN_PATH
from datasmash._version import __version__

#from d3m_metadata import container, hyperparams, metadata as metadata_module, params, utils
from d3m.metadata import hyperparams, params, base
from d3m.container import dataset, numpy
from d3m.primitive_interfaces.base import CallResult, DockerContainer
from d3m.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase


Inputs = dataset.Dataset
Outputs = numpy.ndarray


class Params(params.Params):
    """
    a no-op
    """
    pass


class Hyperparams(hyperparams.Hyperparams):
    """
    a no-op
    """
    pass


class d3m_SmashClassification(SupervisedLearnerPrimitiveBase[Inputs, Outputs,
                                                         Params, Hyperparams]):
    """

    """
    __author__ = "UChicago"
    metadata = base.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.d3m_SmashClassification",
        "primitive_family": "TIME_SERIES_CLASSIFICATION",
        "python_path": "d3m.primitives.datasmash.d3m_SmashClassification",
        "source": {'name': 'UChicago'},
        "version": __version__,
        "id": "2273710f-5306-4dc1-888c-a928d8e7f205",
        "installation": [
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
            'classification',
            'parameter-free',
            'hyperparameter-free'
        ]
    })



    def __init__(self, *,
                 hyperparams: Hyperparams,
                 random_seed: int = 0,
                 docker_containers: Dict[str, DockerContainer] = None,
                 _verbose: int = 0) -> None:

        super().__init__(hyperparams=hyperparams, random_seed=random_seed,
                         docker_containers=docker_containers)

        assert os.path.isfile(os.path.join(BIN_PATH, 'smashmatch')), "invalid bin path."
        self._bin_path = os.path.abspath(os.path.join(BIN_PATH, 'smashmatch'))
        self._channel_parameter_map = {}
        self._cwd = os.getcwd()
        self._d3m_reader = D3MDatasetLoader()
        self._tmp_dir = ''
        self._channel_dirs = []
        self._class_list = []
        self._selected_channels = set()
        self._detrending = False
        self._channel_probabilities = {}
        self._channel_predictions = {}
        self._cluster = False
        self._channels = None
        self._fitted = False

    #@property
    #def selected_channels(self):
    #    return self._selected_channels

    #@selected_channels.setter
    #def selected_channels(self, channels):
    #    if not isinstance(channels, list):
    #        channels_ = [channels]
    #    else:
    #        channels_ = channels
    #    channels_ = ['channel_' + str(c) for c in channels_]
    #    self._selected_channels = set(channels_)

    def set_training_data(self, *,
                          inputs: Inputs,
                          outputs: Outputs
                         ) -> None:
        """
        outputs argument should be specified as None
        """
        self._d3m_reader.load_dataset(data=inputs,
                                      train_or_test='train')
        self._tmp_dir, self._channel_dirs, self._class_list, _ = (
            self._d3m_reader.write_libs(problem_type='supervised'))
        self._fitted = False

    def _fit_one_channel(self, directory):
        """

        """
        qtz = Quantizer(problem_type='supervised', multi_partition=False)
        X = qtz.fit_transform(directory, output_type='filename')
        return X, qtz

    def fit(self, *,
            timeout: float = None,
            iterations: int = None
           ) -> CallResult[None]:
        """

        """
        if self._fitted:
            return CallResult(None)

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
            #order, param_dict_list, qlib_dirs = quantizer(channel_dir,
            #                                              use_genesess=False,
            #                                              problem_type='supervised')
            #channel_info = {}
            #channel_info['quantizer_order'] = order
            #channel_info['parameters'] = param_dict_list
            #channel_info['qlib_directories'] = qlib_dirs

            X, qtz = self._fit_one_channel(channel_dir)
            channel_name = os.path.basename(channel_dir)
            self._channel_parameter_map[channel_name] = (X, qtz)

        #if verbose:
        #    print('Chosen partition:')
        #    pprint_dict(self._channel_partition_map)

        self._fitted = True
        return CallResult(None)

    def produce(self, *,
                inputs: Inputs,
                timeout: float = None,
                iterations: int = None
               ) -> CallResult[Outputs]:
        """

        """
        current_partition = self._channel_parameter_map
        self._d3m_reader.load_dataset(data=inputs,
                                      train_or_test='test')

        #channels = self._channels
        #if channels is not None:
        #    if not isinstance(channels, list):
        #        channels = [channels]
        #    if bool(self._selected_channels):
        #        for channel in channels:
        #            if channel not in self._selected_channels:
        #                raise ValueError("The partition was not found for this "
        #                                 "channel. Re-run 'fit()' with this "
        #                                 "channel included before running "
        #                                 "'produce()' with this channel.")

        channel_problems = self._d3m_reader.write_test()

        for channel, problem in channel_problems.items():
            #if self._channels is not None:
            #    channels_ = ['channel_' + str(c) for c in channels]
            #    if channel not in channels_:
            #        #if verbose:
            #        print('Excluding', channel, '...')
            #        continue
            #elif bool(self._selected_channels) and (channel not in
            #    self._selected_channels):
            #    #if verbose:
            #    print('Excluding', channel, '...')
            #    continue

            #if verbose:
            #start = time.time()
            test_file = problem['test']
            lib_files, qtz = current_partition[channel]
            X = qtz.transform(test_file, output_type='filename')
            #X.to_csv(test_file, sep=' ', index=False, header=False)
            #quantize_inplace(test_file, current_partition[channel],
            #                 pruning=self._prune_range,
            #                 detrending=self._detrending,
            #                 normalization=self._normalization)

            #lib_files = problem['raw_libs']
            output_prefix = os.path.join(self._tmp_dir, 'test', channel, 'out')
            smashmatch(X, lib_files=lib_files,
                       output_prefix=output_prefix)

            out_prob = np.loadtxt(output_prefix + '_prob')

            dist_files = [output_prefix + '_' + lib_file.split('/')[-1] for lib_file
                          in lib_files]

            out_class_raw = np.loadtxt(output_prefix + '_class')
            out_class = []
            for i in out_class_raw:
                out_class.append(self._d3m_reader.index_class_map[int(i)])

            self._channel_probabilities[channel] = out_prob
            self._channel_predictions[channel] = out_class
            #if verbose:
            #    print('CHANNEL ' + channel.split('_')[-1] + ' DONE')
            #    print(out_class)
            #    end = time.time()
            #    print('TIME:', end - start, '\n')
        prob_list = list(self._channel_probabilities.values())
        predictions = argmax_prod_matrix_list(prob_list,
                                              index_class_map=self._d3m_reader.index_class_map)

        return CallResult(predictions)

    #@property
    #def channel_predictions(self):
    #    return self._channel_predictions

    def get_params(self) -> Params:
        """
        A noop
        """
        return None

    def set_params(self, *, params: Params) -> None:
        """
        A noop
        """
        return None

