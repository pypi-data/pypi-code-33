import time
import os
import subprocess as sp
import numpy as np
import pandas as pd
import json
from typing import Dict, Optional
from sklearn.cluster import KMeans
from datasmash.d3m_dataset_loader import D3MDatasetLoader
from datasmash.utils import smash, smashmatch
from datasmash.quantizer import Quantizer, fit_one_channel
from datasmash.utils import pprint_dict, argmax_prod_matrix_list
from datasmash.config import CWD, BIN_PATH
from datasmash._version import __version__

from d3m.metadata import hyperparams, params, base
from d3m import container
from d3m.primitive_interfaces.base import CallResult, DockerContainer
from d3m.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase


Inputs = container.Dataset
Outputs = container.DataFrame

class Params(params.Params):
    quantizer_params: Optional[dict]


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


class d3m_GSmashClassification(SupervisedLearnerPrimitiveBase[Inputs, Outputs,
                                                         Params, Hyperparams]):
    """

    """
    __author__ = "UChicago"
    metadata = base.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.d3m_GSmashClassification",
        "primitive_family": "TIME_SERIES_CLASSIFICATION",
        "python_path": "d3m.primitives.datasmash.d3m_GSmashClassification",
        "source": {
        	'name': 'UChicago',
			'contact': 'mailto:virotaru@uchicago.edu'
		},
        "version": __version__,
        "id": "fe8da525-2bd1-42b2-ace8-b34769511b28",
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
            'classification',
            'parameter-free',
            'hyperparameter-free'
        ]
    })



    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed)


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
        self._inplace = True
        self._channel_probabilities = {}
        self._channel_predictions = {}
        self._cluster = False
        self._channels = None
        self._quantizer_core_hours = self.hyperparams['quantizer_core_hours']
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

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        """
        outputs argument should be specified as None
        """
        print('Datasmash version:',__version__)
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='train')
        self._tmp_dir, self._channel_dirs, self._class_list, _ = (
            self._d3m_reader.write_libs(problem_type='supervised'))
        self._fitted = False

    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
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
            X, qtz = fit_one_channel(channel_dir, problem_type='supervised',
                                     #multi_partition=False,
                                     num_quantizations=1,
                                     gsmash=True,
                                     core_hours=self._quantizer_core_hours)
            channel_name = os.path.basename(channel_dir)
            self._channel_parameter_map[channel_name] = (X, qtz)

        #if verbose:
        #    print('Chosen partition:')
        #    pprint_dict(self._channel_partition_map)

        self._fitted = True
        return CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None,
                iterations: int = None) -> CallResult[Outputs]:
        """

        """
        print('Datasmash version:',__version__)
        print('Hacky loader\n')
        stri = str(inputs)
        str_list = stri.split('\'')
        for stri in str_list:
            if stri.find('file:///')>=0:
                inputs = stri[7:]
        partition_check = bool(self._channel_parameter_map) or (partition is not None)
        assert partition_check, "partition must be found via 'fit()' or inputted"
        #if partition is not None:
        #    current_partition = partition
        #elif self.channel_partition_map is not None:
        current_partition = self._channel_parameter_map
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='test')

        if self._channels is not None:
            if not isinstance(channels, list):
                channels = [channels]
            if bool(self._selected_channels):
                for channel in channels:
                    if channel not in self._selected_channels:
                        raise ValueError("The partition was not found for this "
                                         "channel. Re-run 'fit()' with this "
                                         "channel included before running "
                                         "'produce()' with this channel.")

        channel_problems = self._d3m_reader.write_test()

        #smashmatch = [self._bin_path]
        for channel, problem in channel_problems.items():
            if self._channels is not None:
                channels_ = ['channel_' + str(c) for c in channels]
                if channel not in channels_:
                    #if verbose:
                    print('Excluding', channel, '...')
                    continue
            elif bool(self._selected_channels) and (channel not in
                self._selected_channels):
                #if verbose:
                print('Excluding', channel, '...')
                continue

            #if verbose:
            #start = time.time()
            #test_file = problem[0]
            #qtz = current_partition[channel]
            #X = qtz.transform(test_file)
            #X.to_csv(test_file, sep=' ', index=False, header=False)
            #quantize_inplace(test_file, current_partition[channel],
            #                 pruning=self._prune_range,
            #                 detrending=self._detrending,
            #                 normalization=self._normalization)

            #partition = []
            #dtype = ['-T', 'symbolic']
            #else:
            #    error_msg = ("keyword-only argument 'data_type' must be set if"
            #                 "'inplace' keyword-only argument of 'fit()'"
            #                 "method was set to False")
            #    assert data_type is not None, error_msg
            #    partition = ['-P'] + current_partition[channel]
            #    dtype = ['-T', data_type]
            test_file = problem['test']
            lib_files, qtz = current_partition[channel]
            X = qtz.transform(test_file, output_type='filename')
            #file_in = ['-f', test_file, '-F'] + lib_files
            #file_out = ['-o', output_prefix]
            #constants = dtype + ['-D', 'row']
            #_num_reruns = ['-n', nr]
            #command_list = (smashmatch + file_in + file_out + constants + partition
            #                + _num_reruns)
            output_prefix = os.path.join(self._tmp_dir, 'test', channel, 'out')
            smashmatch(X, lib_files=lib_files,
                       output_prefix=output_prefix)

            #sp.check_output(command_list)
            out_prob = np.loadtxt(output_prefix + '_prob')

            dist_files = [output_prefix + '_' + lib_file.split('/')[-1] for lib_file
                          in lib_files]
            #distances = []
            #for dist_file in dist_files:
            #    distances.append(np.loadtxt(dist_file))
            #out_class_raw = np.argmin(np.array(distances), axis=0)

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
        predictions = np.array(predictions)
        with open(inputs, 'r') as inputFile:
            datasetSchema = json.load(inputFile)
            inputFile.close()
        dataResources = datasetSchema['dataResources']

        table = next(dataResources[i] for i in range(len(dataResources)) if dataResources[i]['resType'] == 'table')
        tablePath = table['resPath']
        d3mIndex = pd.read_csv(os.path.join(os.path.dirname(inputs), tablePath), usecols=['d3mIndex'])
        trainTargetsCatLabel = next(dataResources[i]['resPath'] for i in range(len(dataResources)) if dataResources[i]['resType'] == 'table')
        for column in table['columns']:
            if 'suggestedTarget' in column['role']:
                trainTargetsCatLabel = column['colName']


        to_return = pd.DataFrame({'d3mIndex':d3mIndex['d3mIndex'], trainTargetsCatLabel:predictions})           
        return CallResult(container.DataFrame(to_return, generate_metadata=False))


    #@property
    #def channel_predictions(self):
    #    return self._channel_predictions

    def get_params(self) -> Params:
        
        return Params(
                    quantizer_params=self.__dict__)


    def set_params(self, *, params: Params) -> None:
        self.__dict__ = params['quantizer_params']