#from zed_base import SmashBase
#
#
#class SmashClassification(SmashBase):
#    """
#
#    """
#    def __init__(self, ):
#
#        , *, problem_type='supervised', multi_partition=False,
#                 output_type=F

import os
import time
import numpy as np
import pandas as pd
from datasmash.quantizer import Quantizer, mkqdir, vectorize_label
from datasmash.utils import smashmatch, pprint_dict, argmax_prod_matrix_list
from datasmash.config import CWD, BIN_PATH


class SmashClassification():
    """

    """
    def __init__(self, *, multi_partition=False):
        smashmatch_path = os.path.join(BIN_PATH, 'smashmatch')
        assert os.path.isfile(os.path.join(BIN_PATH, 'smashmatch')), "invalid bin path."
        self._tmp_dir = ''
        self.quantizer = Quantizer(problem_type='supervised',
                                   multi_partition=multi_partition)
        self._fitted = False

    def fit(self, X, y):
        """

        """
        self._tmp_dir = mkqdir(X, labels=y, parent_dir='./')
        y_ = vectorize_label(X, y)
        X_ = self.quantizer.fit_transform(self._tmp_dir)

    def predict(self, X):
        """

        """


#
#
#
#    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
#        """
#        outputs argument should be specified as None
#        """
#        self._d3m_reader.load_dataset(data=inputs,
#                                     train_or_test='train')
#        self._tmp_dir, self._channel_dirs, self._class_list = (
#            self._d3m_reader.write_libs(problem_type='supervised'))
#        self._fitted = False
#
#    def _fit_one_channel(self, directory):
#        """
#
#        """
#        prune_range, detrending, normalization, partition = quantizer(directory,
#                                                                      inplace=True,
#                                                                      use_genesess=False,
#                                                                      problem_type='supervised')
#        self._prune_range = prune_range
#        self._detrending = detrending
#        self._normalization = normalization
#
#        return partition
#
#    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
#        """
#
#        """
#        if self._fitted:
#            return CallResult(None)
#
#        channels = self._channels
#        if channels is not None:
#            if channels == -1:
#                pass
#            elif not isinstance(channels, list):
#                channels = [channels]
#            selected_channels = ['channel_' + str(c) for c in channels]
#            self._selected_channels = set(selected_channels)
#        elif bool(self._selected_channels):
#            selected_channels = self._selected_channels
#        else:
#            selected_channels = self._channel_dirs
#
#        for channel_dir in selected_channels:
#            partition = self._fit_one_channel(channel_dir)
#            channel_name = channel_dir.split('/')[-1]
#            self._channel_partition_map[channel_name] = partition
#
#        #if verbose:
#        #    print('Quantizing in place:', self._inplace)
#        #    print('Chosen partition:')
#        #    pprint_dict(self._channel_partition_map)
#
#        self._fitted = True
#        return CallResult(None)
#
#    def produce(self, *, inputs: Inputs, timeout: float = None,
#                iterations: int = None) -> CallResult[Outputs]:
#        """
#
#        """
#        #if partition is not None:
#        #    current_partition = partition
#        #elif self.channel_partition_map is not None:
#        current_partition = self._channel_partition_map
#        self._d3m_reader.load_dataset(data=inputs,
#                                     train_or_test='test')
#
#        channels = self._channels
#        if channels is not None:
#            if not isinstance(channels, list):
#                channels = [channels]
#            if bool(self._selected_channels):
#                for channel in channels:
#                    if channel not in self._selected_channels:
#                        raise ValueError("The partition was not found for this "
#                                         "channel. Re-run 'fit()' with this "
#                                         "channel included before running "
#                                         "'produce()' with this channel.")
#
#        channel_problems = self._d3m_reader.write_test()
#
#        for channel, problem in channel_problems.items():
#            if self._channels is not None:
#                channels_ = ['channel_' + str(c) for c in channels]
#                if channel not in channels_:
#                    #if verbose:
#                    print('Excluding', channel, '...')
#                    continue
#            elif bool(self._selected_channels) and (channel not in
#                self._selected_channels):
#                #if verbose:
#                print('Excluding', channel, '...')
#                continue
#
#            #if verbose:
#            start = time.time()
#            test_file = problem[0]
#            quantize_inplace(test_file, current_partition[channel],
#                             pruning=self._prune_range,
#                             detrending=self._detrending,
#                             normalization=self._normalization)
#
#            #partition = []
#            #dtype = ['-T', 'symbolic']
#            #else:
#            #    error_msg = ("keyword-only argument 'data_type' must be set if"
#            #                 "'inplace' keyword-only argument of 'fit()'"
#            #                 "method was set to False")
#            #    assert data_type is not None, error_msg
#            #    partition = ['-P'] + current_partition[channel]
#            #    dtype = ['-T', data_type]
#            lib_files = problem[1]
#            #file_in = ['-f', test_file, '-F'] + lib_files
#            output_prefix = os.path.join(self._tmp_dir, 'test', channel, 'out')
#            #file_out = ['-o', output_prefix]
#            #constants = dtype + ['-D', 'row']
#            #_num_reruns = ['-n', nr]
#            #command_list = (smashmatch + file_in + file_out + constants + partition
#            #                + _num_reruns)
#            print('TESTING')
#            smashmatch(test_file, lib_files=lib_files,
#                       output_prefix=output_prefix)
#            print('TESTING')
#
#            #sp.check_output(command_list)
#            out_prob = np.loadtxt(output_prefix + '_prob')
#
#            dist_files = [output_prefix + '_' + lib_file.split('/')[-1] for lib_file
#                          in lib_files]
#            #distances = []
#            #for dist_file in dist_files:
#            #    distances.append(np.loadtxt(dist_file))
#            #out_class_raw = np.argmin(np.array(distances), axis=0)
#
#            out_class_raw = np.loadtxt(output_prefix + '_class')
#            out_class = []
#
#            for i in out_class_raw:
#                out_class.append(self._d3m_reader.index_class_map[int(i)])
#
#            self._channel_probabilities[channel] = out_prob
#            self._channel_predictions[channel] = out_class
#            #if verbose:
#            #    print('CHANNEL ' + channel.split('_')[-1] + ' DONE')
#            #    print(out_class)
#            #    end = time.time()
#            #    print('TIME:', end - start, '\n')
#        prob_list = list(self._channel_probabilities.values())
#        predictions = argmax_prod_matrix_list(prob_list,
#                                              index_class_map=self._d3m_reader.index_class_map)
#
#        return CallResult(predictions)
#
#    #@property
#    #def channel_predictions(self):
#    #    return self._channel_predictions
#
#    def get_params(self) -> Params:
#        """
#        A noop
#        """
#        return None
#
#    def set_params(self, *, params: Params) -> None:
#        """
#        A noop
#        """
#        return None
#
