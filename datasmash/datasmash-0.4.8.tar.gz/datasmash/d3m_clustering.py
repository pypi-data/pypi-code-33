import os
import csv
import time
import subprocess as sp
import numpy as np
import pandas as pd
import json
from typing import Dict, Optional
from sklearn.cluster import KMeans
from datasmash.utils import (pprint_dict, smash, smashmatch,
                             matrix_list_p_norm, argmax_prod_matrix_list)
from datasmash.d3m_dataset_loader import D3MDatasetLoader
from datasmash.quantizer import Quantizer, fit_one_channel
from datasmash.config import CWD, BIN_PATH
from datasmash._version import __version__

from d3m.metadata import hyperparams, params, base
from d3m import container
from d3m.primitive_interfaces.base import CallResult, DockerContainer
from d3m.primitive_interfaces.clustering import ClusteringLearnerPrimitiveBase


Inputs = container.Dataset
Outputs = container.DataFrame


class Params(params.Params):
    quantizer_params: Optional[dict]


class Hyperparams(hyperparams.Hyperparams):
    n_clusters = hyperparams.Hyperparameter[int](
        default = 2,
        description = 'Number of clusters per class. ',
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter']
    )
    quantizer_core_hours = hyperparams.Bounded(
        default = 28,
        lower = 1,
        upper = None,
        description = ('Number of core-hours one wishes to allot to the'
                       + ' QUANTIZATION PORTION of the algorithm.'),
        semantic_types = ['https://metadata.datadrivendiscovery.org/types/TuningParameter',
                          'https://metadata.datadrivendiscovery.org/types/ResourcesUseParameter']
    )


class d3m_SmashClustering(ClusteringLearnerPrimitiveBase[Inputs, Outputs, Params,
                                              Hyperparams]):
    """

    """
    __author__ = "UChicago"
    metadata = base.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.d3m_SmashClustering",
        "primitive_family": "CLUSTERING",
        "python_path": "d3m.primitives.datasmash.d3m_SmashClustering",
        "source": {
        	'name': 'UChicago',
			'contact': 'mailto:virotaru@uchicago.edu'
		},
        "version": __version__,
        "id": "74767ad3-ac44-4d20-9c1c-248f56a42428",
        "installation": [
            {'type': base.PrimitiveInstallationType.PIP,
             'package': 'datasmash',
             'version': __version__
            }
        ],
        "hyperparameters_to_tune": [
            "n_clusters"
        ],
        "keywords": [
            'time',
            'series',
            'data smashing',
            'data-smashing',
            'data_smashing',
            'datasmashing',
            'clustering',
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

        assert os.path.isfile(os.path.join(BIN_PATH, 'smash')), (
               "invalid smash bin path")
        assert os.path.isfile(os.path.join(BIN_PATH, 'smashmatch')), (
               "invalid smashmatch bin path")
        self._bin_path_smash = os.path.abspath(os.path.join(BIN_PATH, 'smash'))
        self._bin_path_smashmatch = os.path.abspath(os.path.join(BIN_PATH,
                                                                'smashmatch'))
        self._cwd = os.getcwd()
        self._d3m_reader = D3MDatasetLoader()
        self._tmp_dir = ''
        self._partition = None
        self._num_streams = 0
        self._lib_files = {}
        self._channel_dirs = []
        self._channel_parameter_map = {}
        self._selected_channels = set()
        self._channel_probabilities = {}
        self._channel_predictions = {}
        self._detrending = False
        self._channels = None
        self._fitted = False

        self._quantizer_core_hours = self.hyperparams['quantizer_core_hours']
        self._n_clusters = self.hyperparams['n_clusters']
        #if cluster_class is None:
        self._cluster_class = KMeans(n_clusters=self._n_clusters)
        #else:
        #    self._cluster_class = cluster_class

    def set_training_data(self, *, inputs: Inputs) -> None:
        """
        outputs argument should be specified as None
        """
        print('Datasmash version:',__version__)
        print('Hacky loader\n')
        stri = str(inputs)
        str_list = stri.split('\'')
        for stri in str_list:
            if stri.find('file:///')>=0:
                inputs = stri[8:]
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='train')
        self._tmp_dir, self._channel_dirs, self._num_streams = (
            self._d3m_reader.write_libs(problem_type='unsupervised'))

        self._fitted = False

    #def _fit_one_channel(self, directory):
    #    """

    #    """
    #    #prune_range, detrending, normalization, partition = quantizer(directory,
    #    #                                                              inplace=True,
    #    #                                                              use_genesess=False,
    #    #                                                              problem_type='unsupervised',
    #    #                                                              num_streams=self._num_streams,)
    #    #self._prune_range = prune_range
    #    #self._detrending = detrending
    #    #self._normalization = normalization

    #    #return partition
    #    qtz = Quantizer(problem_type='supervised', multi_partition=False)
    #    X = qtz.fit_transform(directory, output_type='filename')
    #    return X, qtz

    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        """

        """
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
                                     multi_partition=False,
                                     core_hours=self._quantizer_core_hours)
            channel_name = os.path.basename(channel_dir)
            self._channel_parameter_map[channel_name] = (X, qtz)

        #if verbose:
        #    print('Chosen partition:')
        #    pprint_dict(self._channel_parameter_map)

        # run smash to get the distance matrix

        distance_matrices = []
        for channel_dir, (X, qtz) in self._channel_parameter_map.items():
            channel_path = os.path.join(self._tmp_dir, channel_dir)
            #input_data = os.path.join(channel_path, 'dataset')
            output_file = os.path.join(channel_path, 'H.dst')
            #results = smash(input_data, outfile=output_file)
            results = smash(X[0], outfile=output_file)
            distance_matrices.append(results)
        final_dist_matrix = matrix_list_p_norm(distance_matrices, p=2)
        final_dist_matrix_path = os.path.join(self._tmp_dir, 'H_final.dst')
        np.savetxt(final_dist_matrix_path, final_dist_matrix)

        # run clustering algo to get clusters, use these clusters as targets
        # and save the original time series with the targets to form a
        # smashmatch problem
        cluster_assignments = self._cluster_class.fit_predict(final_dist_matrix)
        cluster_assignments = pd.DataFrame(cluster_assignments,
                                           columns=['cluster'])
        for channel_dir in self._channel_dirs:
            dataset_path = self._channel_parameter_map[os.path.basename(channel_dir)][0][0]
            train_data = pd.read_csv(dataset_path, delimiter=' ', header=None)
            train_data = pd.concat([train_data, cluster_assignments], axis=1)
            train_data.to_csv('test')
            cluster_list = train_data['cluster'].unique().tolist()
            channel_name = channel_dir.split('/')[-1]
            self._lib_files[channel_name] = []
            for i in cluster_list:
                train_data_i = train_data[train_data['cluster']==i].iloc[:, :-1]
                lib_name = os.path.join(channel_dir, 'train_cluster_' + str(i))
                #lib_path = os.path.join(self._tmp_dir, lib_name)
                #for row in train_data_i:
                #    with open(lib_path, 'a') as outfile:
                #        wr = csv.writer(outfile, delimiter=' ',
                #                        quoting=csv.QUOTE_NONE)
                #        wr.writerow(row)
                train_data_i.to_csv(lib_name, sep=' ', header=False,
                                    index=False)
                self._lib_files[channel_name].append(lib_name)

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
        current_partition = self._channel_parameter_map
        self._d3m_reader.load_dataset(data=inputs,
                                     train_or_test='test')

        channels = self._channels
        if channels is not None:
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

        for channel, problem in channel_problems.items():
            if channels is not None:
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
            start = time.time()
            test_file = problem['test']
            _, qtz = current_partition[channel]
            lib_files = self._lib_files[channel]
            X = qtz.transform(test_file, output_type='filename')
            #X.to_csv(test_file, sep=' ', index=False, header=False)
            #quantize_inplace(test_file, current_partition[channel],
            #                 pruning=self._prune_range,
            #                 detrending=self._detrending,
            #                 normalization=self._normalization)

            #lib_files = self._lib_files[channel]
            output_prefix = os.path.join(self._tmp_dir, 'test', channel, 'out')
            smashmatch(X, lib_files=lib_files,
                       output_prefix=output_prefix)

            out_prob = np.loadtxt(output_prefix + '_prob')
            out_class_raw = np.loadtxt(output_prefix + '_class')
            if self._d3m_reader.class_list:
                index_class_map = self._d3m_reader.index_class_map
                out_class = []
                for i in out_class_raw:
                    out_class.append(self._d3m_reader.index_class_map[int(i)])
            else:
                index_class_map = None
                out_class = out_class_raw

            self._channel_probabilities[channel] = out_prob
            #if verbose:
            print('CHANNEL ' + channel.split('_')[-1] + ' DONE')
            end = time.time()
            print('TIME:', end - start, '\n')
        prob_list = list(self._channel_probabilities.values())

        predictions = argmax_prod_matrix_list(prob_list,
                                              index_class_map=index_class_map)
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