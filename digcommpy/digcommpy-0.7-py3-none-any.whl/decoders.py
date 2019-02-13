from abc import ABC, abstractmethod
import inspect
import pickle

import numpy as np
from joblib import Parallel, delayed, cpu_count
from sklearn import svm
from hpelm import ELM
from keras import layers
from keras.models import Sequential
from keras.utils.np_utils import to_categorical

from .messages import unpack_to_bits, pack_to_dec, generate_data
from .encoders import PolarEncoder, Encoder, PolarWiretapEncoder
from .modulators import Modulator


def _logdomain_sum(x, y):
    if x < y:
        z = y + np.log1p(np.exp(x-y))
    else:
        z = x + np.log1p(np.exp(y-x))
    return z

def _logdomain_sum_multiple(x, y):
    _logpart = np.log1p(np.exp(-np.abs(x-y)))
    z = np.maximum(x, y) + _logpart
    return z


class Decoder(ABC):
    """Abstract decoder class."""
    def __init__(self, code_length, info_length, base=2, parallel=True):
        self.code_length = code_length
        self.info_length = info_length
        self.base = base
        self.parallel = parallel

    @abstractmethod
    def decode_messages(self, messages, channel=None): pass


class IdentityDecoder(Decoder):
    """Identity decoder. Simply returns the input."""
    @staticmethod
    def decode_messages(messages, channel=None):
        return messages


class RepetitionDecoder(Decoder):
    def __init__(self, *args, **kwargs): pass

    @staticmethod
    def decode_messages(messages, channel=None):
        decoded = np.zeros((len(messages), 1))
        for idx, message in enumerate(messages):
            val, counts = np.unique(message, return_counts=True)
            _decision = np.argmax(counts)
            decoded[idx] = val[_decision]
        return decoded


class LinearDecoder(Decoder):
    """Linear block decoder.

    Parameters
    ----------
    TODO
    """
    def decode_messages(self, messages, channel=None):
        raise NotImplementedError()


class PolarDecoder(Decoder):
    """Polar code decoder. Taken from **polarcodes.com**

    The decoder for BAWGN channels expects a channel output of noisy codewords
    which are modulated to +1 and -1.

    Parameters
    ----------
    code_length : int
        Length of the code.

    info_length : int
        Length of the messages.

    design_channel : str
        Name of the used channel. Valid choices are currently "BAWGN" and "BSC".

    design_channelstate : float, optional
        State of the design channel. For "BAWGN" channels, this corresponds to
        the SNR value in dB. For "BSC" channels, this corresponds to the
        bit-flip probability.

    pos_lookup : array, optional
        Position lookup of the polar code, where -1 indicates message bits,
        while 0 and 1 denote the frozenbits.

    frozenbits : array, optional
        Bits used for the frozen bit positions. This is ignored, if `pos_lookup`
        is provided.

    parallel : bool, optional
        If True, parallel processing is used. This might not be available on
        all machines and causes higher use of system resources.
    """
    def __init__(self, code_length, info_length, design_channel,
                 design_channelstate=0., pos_lookup=None, frozenbits=None,
                 parallel=True, **kwargs):
        self.design_channel = design_channel.upper()
        self.design_channelstate = design_channelstate
        if pos_lookup is None:
            self.pos_lookup = PolarEncoder.construct_polar_code(
                code_length, info_length, design_channel, design_channelstate,
                frozenbits)
        else:
            self.pos_lookup = np.array(pos_lookup)
        self.rev_index = self._reverse_index(code_length)
        self.idx_first_one = self._index_first_num_from_msb(code_length, 1)
        self.idx_first_zero = self._index_first_num_from_msb(code_length, 0)
        super().__init__(code_length, info_length, parallel=parallel)

    @staticmethod
    def _reverse_index(code_length):
        _n = int(np.ceil(np.log2(code_length)))
        rev_idx = [pack_to_dec(np.flip(unpack_to_bits([idx], _n), axis=1))[0][0]
                   for idx in range(code_length)]
        return rev_idx

    @staticmethod
    def _index_first_num_from_msb(code_length, number):
        _n = int(np.ceil(np.log2(code_length)))
        idx_list = np.zeros(code_length)
        for idx in range(code_length):
            idx_bin = unpack_to_bits([idx], _n)[0]
            try:
                last_level = np.where(idx_bin == number)[0][0]
            except IndexError:
                last_level = _n-1
            idx_list[idx] = last_level
        return idx_list

    def decode_messages(self, messages, channel):
        #decoded = np.zeros((len(messages), self.info_length))
        decoded = np.zeros((len(messages), self.code_length))
        if self.design_channel == "BAWGN":
            channel_state = channel.snr_db
            snr = 10**(channel_state/10.)
            initial_llr = -2*np.sqrt(2*(self.info_length/self.code_length)*snr)*messages
            #if self.parallel:
            #    num_cores = cpu_count()
            #    decoded = Parallel(n_jobs=num_cores)(
            #        delayed(self._polar_llr_decode)(k) for k in initial_llr)
            #    decoded = np.array(decoded)
            #else:
            #    for idx, _llr_codeword in enumerate(initial_llr):
            #        decoded[idx] = self._polar_llr_decode(_llr_codeword)
            decoded = self._polar_llr_decode_multiple(initial_llr)
        elif self.design_channel == "BSC":
            #_bitflip = self.channel_state
            _bitflip = channel.prob
            llr = np.log(_bitflip) - np.log(1-_bitflip)
            initial_llr = (2*messages - 1) * llr
            if self.parallel:
                num_cores = cpu_count()
                decoded = Parallel(n_jobs=num_cores)(
                    delayed(self._polar_llr_decode)(k) for k in initial_llr)
                decoded = np.array(decoded)
            else:
                for idx, _llr_codeword in enumerate(initial_llr):
                    decoded[idx] = self._polar_llr_decode(_llr_codeword)
        decoded = self._get_info_bit_positions(decoded)
        return decoded

    def _get_info_bit_positions(self, decoded):
        return decoded[:, self.pos_lookup == -1]

    def _polar_llr_decode(self, initial_llr):
        llr = np.zeros(2*self.code_length-1)
        llr[self.code_length-1:] = initial_llr
        bit_branch = np.zeros((2, self.code_length-1))
        decoded = np.zeros(self.code_length)
        for j in range(self.code_length):
            rev_idx = self.rev_index[j]
            llr = self._update_llr(llr, bit_branch, rev_idx)
            if self.pos_lookup[rev_idx] == -1:
                if llr[0] > 0:
                    decoded[rev_idx] = 0
                else:
                    decoded[rev_idx] = 1
            else:
                decoded[rev_idx] = self.pos_lookup[rev_idx]
            bit_branch = self._update_bit_branch(decoded[rev_idx], rev_idx, bit_branch)
        #return decoded[self.pos_lookup == -1]
        return decoded

    def _update_llr(self, llr, bit_branch, rev_idx):
        _n = int(np.ceil(np.log2(self.code_length)))
        if rev_idx == 0:
            next_level = _n
        else:
            last_level = int(self.idx_first_one[rev_idx]+1)
            st = int(2**(last_level-1))
            ed = int(2**(last_level)-1)
            for idx in range(st-1, ed):
                llr[idx] = self._lowerconv(
                    bit_branch[0, idx], llr[ed+2*(idx+1-st)], llr[ed+2*(idx+1-st)+1])
            next_level = last_level - 1
        for level in np.arange(next_level, 0, -1):
            st = int(2**(level-1))
            ed = int(2**(level) - 1)
            for idx in range(st-1, ed):
                llr[idx] = self._upperconv(llr[ed+2*(idx+1-st)], llr[ed+2*(idx+1-st)+1])
        return llr

    @staticmethod
    def _lowerconv(upper_decision, upper_llr, lower_llr):
        if upper_decision == 0:
            llr = lower_llr + upper_llr
        else:
            llr = lower_llr - upper_llr
        return llr

    @staticmethod
    def _upperconv(llr1, llr2):
        llr = _logdomain_sum(llr1+llr2, 0) - _logdomain_sum(llr1, llr2)
        return llr

    def _update_bit_branch(self, bit, rev_idx, bit_branch):
        _n = int(np.ceil(np.log2(self.code_length)))
        if rev_idx == self.code_length-1:
            return
        elif rev_idx < self.code_length/2:
            bit_branch[0, 0] = bit
        else:
            last_level = int(self.idx_first_zero[rev_idx]+1)
            bit_branch[1, 0] = bit
            for level in range(1, last_level-2+1):
                st = int(2**(level-1))
                ed = int(2**(level)-1)
                for idx in range(st-1, ed):
                    bit_branch[1, ed+2*(idx+1-st)] = np.mod(bit_branch[0, idx]+bit_branch[1, idx], 2)
                    bit_branch[1, ed+2*(idx+1-st)+1] = bit_branch[1, idx]
            level = last_level-1
            st = int(2**(level-1))
            ed = int(2**(level)-1)
            for idx in range(st-1, ed):
                bit_branch[0, ed+2*(idx+1-st)] = np.mod(bit_branch[0, idx]+bit_branch[1, idx], 2)
                bit_branch[0, ed+2*(idx+1-st)+1] = bit_branch[1, idx]
        return bit_branch

#####
    def _polar_llr_decode_multiple(self, initial_llr):
        llr = np.zeros((len(initial_llr), 2*self.code_length-1))
        llr[:, self.code_length-1:] = initial_llr
        bit_branch = np.zeros((len(initial_llr), 2, self.code_length-1))
        decoded = np.zeros((len(initial_llr), self.code_length))
        for j in range(self.code_length):
            rev_idx = self.rev_index[j]
            llr = self._update_llr_multiple(llr, bit_branch, rev_idx)
            if self.pos_lookup[rev_idx] == -1:
                #decoded[:, rev_idx] = 0
                _idx = np.where(llr[:, 0] <= 0)[0]
                decoded[_idx, rev_idx] = 1
            else:
                decoded[:, rev_idx] = self.pos_lookup[rev_idx]
            bit_branch = self._update_bit_branch_multiple(
                decoded[:, rev_idx], rev_idx, bit_branch)
        #return decoded[self.pos_lookup == -1]
        return decoded

    def _update_llr_multiple(self, llr, bit_branch, rev_idx):
        _n = int(np.ceil(np.log2(self.code_length)))
        if rev_idx == 0:
            next_level = _n
        else:
            last_level = int(self.idx_first_one[rev_idx]+1)
            st = int(2**(last_level-1))
            ed = int(2**(last_level)-1)
            for idx in range(st-1, ed):
                llr[:, idx] = self._lowerconv_multiple(
                    bit_branch[:, 0, idx], llr[:, ed+2*(idx+1-st)], llr[:, ed+2*(idx+1-st)+1])
            next_level = last_level - 1
        for level in np.arange(next_level, 0, -1):
            st = int(2**(level-1))
            ed = int(2**(level) - 1)
            for idx in range(st-1, ed):
                llr[:, idx] = self._upperconv_multiple(
                    llr[:, ed+2*(idx+1-st)], llr[:, ed+2*(idx+1-st)+1])
        return llr

    def _update_bit_branch_multiple(self, bit, rev_idx, bit_branch):
        _n = int(np.ceil(np.log2(self.code_length)))
        if rev_idx == self.code_length-1:
            return
        elif rev_idx < self.code_length/2:
            bit_branch[:, 0, 0] = bit
        else:
            last_level = int(self.idx_first_zero[rev_idx]+1)
            bit_branch[:, 1, 0] = bit
            for level in range(1, last_level-2+1):
                st = int(2**(level-1))
                ed = int(2**(level)-1)
                for idx in range(st-1, ed):
                    bit_branch[:, 1, ed+2*(idx+1-st)] = np.mod(bit_branch[:, 0, idx]+bit_branch[:, 1, idx], 2)
                    bit_branch[:, 1, ed+2*(idx+1-st)+1] = bit_branch[:, 1, idx]
            level = last_level-1
            st = int(2**(level-1))
            ed = int(2**(level)-1)
            for idx in range(st-1, ed):
                bit_branch[:, 0, ed+2*(idx+1-st)] = np.mod(bit_branch[:, 0, idx]+bit_branch[:, 1, idx], 2)
                bit_branch[:, 0, ed+2*(idx+1-st)+1] = bit_branch[:, 1, idx]
        return bit_branch

    @staticmethod
    def _lowerconv_multiple(upper_decision, upper_llr, lower_llr):
        llr = lower_llr - upper_llr
        idx = np.where(upper_decision == 0)
        llr[idx] = lower_llr[idx] + upper_llr[idx]
        return llr

    @staticmethod
    def _upperconv_multiple(llr1, llr2):
        llr = _logdomain_sum_multiple(llr1+llr2, 0) - _logdomain_sum_multiple(llr1, llr2)
        return llr
####

class PolarWiretapDecoder(PolarDecoder):
    """Decoder class for decoding polar wiretap codes.
    You can either provide both channels (to Bob and Eve) or provide the main
    channel to Bob and the position lookup of the already constructed code.

    Parameters
    ----------
    code_length : int
        Length of the codewords.

    design_channel_bob : str
        Channel name of the main channel to Bob. Valid choices are the channel
        models which are supported by the PolarDecoder.

    design_channelstate_bob : float
        Channelstate of the main channel.

    design_channel_eve : str, optional
        Channel name of the side channel to Eve. Valid choices are the channel
        models which are supported by the PolarEncoder.

    design_channelstate_eve : float, optional
        Channelstate of the side channel.

    pos_lookup : array, optional
        Position lookup of the constructed wiretap code. If this is provided,
        no additional code is constructed and the values of Eve's channel are
        ignored.
    """
    def __init__(self, code_length, design_channel_bob, design_channelstate_bob,
                 design_channel_eve=None, design_channelstate_eve=0.,
                 pos_lookup=None, frozenbits=None, parallel=True, **kwargs):
        if pos_lookup is None:
            pos_lookup = PolarWiretapEncoder.construct_polar_wiretap_code(
                code_length, design_channel_bob, design_channel_eve,
                design_channelstate_bob, design_channelstate_eve, frozenbits)
        info_length = np.count_nonzero(pos_lookup == -1)
        info_length_bob = np.count_nonzero(pos_lookup < 0)
        super().__init__(code_length, info_length, design_channel_bob,
                 design_channelstate=design_channelstate_bob,
                 pos_lookup=pos_lookup, frozenbits=frozenbits,
                 parallel=parallel, **kwargs)


class MachineLearningDecoder(Decoder):
    """Decoder class using Machine Learning algorithms as decoder.


    Parameters
    ----------
    code_length : int
        Length of the block code.

    info_length : int
        Number of information bits.

    training_data : list or tuple (arrays or [Encoder, Modulator])
        Two arrays containing the codewords and corresponding messages (binary)
        or an Encoder class where the whole codebook is used as training data.
    """
    def __init__(self, code_length, info_length, **kwargs):
        super().__init__(code_length, info_length, parallel=False)#, **kwargs)
        self.decoder = self._create_decoder(**kwargs)

    def _create_decoder(**kwargs):
        raise NotImplementedError("The general MachineLearning decoder is not "
                                  "implemented.")

#    def __init__(self, code_length, info_length, training_data, **kwargs):
#        if isinstance(training_data[0], Encoder):
#            training_info = generate_data(info_length)
#            training_info_bit = unpack_to_bits(training_info, info_length)
#            training_code = training_data[0].encode_messages(training_info_bit)
#            if isinstance(training_data[1], Modulator):
#                training_code = training_data[1].modulate_symbols(training_code)
#        else:
#            training_code, training_info_bit = training_data
#            training_info = pack_to_dec(training_info_bit)
#
#        self.decoder = None
#        self._train_system(training_code, training_info, training_info_bit,
#                           **kwargs)
#        super().__init__(code_length, info_length, **kwargs)

    def train_system(self, training_data, **kwargs):
        """Train the ML system using training data.

        Parameters
        ----------
        training_data : list
            List of objects to train the systems. Possible options are: `numpy
            arrays` in order: X, y or `Encoder`, `Modulator`.
            If the `Encoder` is used, all possible information words are
            generated and encoded.

        kwargs : keyword arguments
            All arguments that are accepted by the training method of the used
            algorithm.
        """
        if isinstance(training_data[0], Encoder):
            training_info_bit, training_code = training_data[0].generate_codebook()
            training_info = pack_to_dec(training_info_bit)
            if isinstance(training_data[1], Modulator):
                training_code = training_data[1].modulate_symbols(training_code)
        else:
            training_code, training_info_bit = training_data
            training_info = pack_to_dec(training_info_bit)
        self.decoder = self._train_system(training_code, training_info,
                                          training_info_bit, **kwargs)

    def _train_system(self, training_code, training_info, training_info_bit,
                      **kwargs):
        """Train the ML algorithm"""
        raise NotImplementedError("The general ML decoder is not implemented")

    @staticmethod
    def _create_decoder(model, **kwargs):
        _arguments = inspect.getargspec(model)
        _options = {k: v for k, v in kwargs.items() if k in _arguments.args}
        _decoder = model(**_options)
        return _decoder


class SvmDecoder(MachineLearningDecoder):
    """ Decoder class which uses Support Vector Machines (SVM) for decoding.

    The sklearn.svm implementation is used. All parameters which are accepted
    for creating a SVM can be used here.

    Parameters
    ----------
    C : float, optional
        Penalty score.

    kernel : str, optional
        Kernel function. See the sklearn.svm documentation for implemented 
        kernel functions.

    gamma : float, optional
        Kernel parameter. This might be ignored, depending on the kernel.
    """
#    def __init__(self, code_length, info_length, C=1, kernel='rbf', gamma=1,
#                 **kwargs):
#        pass

    def _create_decoder(self, **kwargs):
        return svm.SVC(**kwargs)

    def _train_system(self, training_code, training_info, training_info_bit,
                      **kwargs):
        _decoder = self.decoder
        _decoder.fit(training_code, np.ravel(training_info))
        return _decoder

    def decode_messages(self, messages, channel=None):
        _pred_info = self.decoder.predict(messages)
        _pred_info_bit = unpack_to_bits(_pred_info, self.info_length)
        return _pred_info_bit

    def __str__(self):
        return "SvmDecoder"

    def __repr__(self):
        return repr(self.decoder)


class ElmDecoder(MachineLearningDecoder):
    """ Decoder class which uses Extreme Learning Machines (ELM) for decoding.

    The hpelm implementation is used. 

    Parameters
    ----------
    neurons : list of tuples
        List of tuples, where each tuple looks like the following: (num_neuron,
        activation). The activation function can be either a string accepted by
        the ELM class or a numpy function. To be precise: the tuple is passed
        to the ELM.add_neurons method. Note that the output layer is linear.
    """
    def __init__(self, code_length, info_length, neurons, **kwargs):
        #TODO:Add some logging and storing of history...
        super().__init__(code_length, info_length, neurons=neurons, **kwargs)

    def _create_decoder(self, neurons, **kwargs):
        _decoder = ELM(self.code_length, self.info_length, **kwargs)
        for _neurons in neurons:
            _decoder.add_neurons(*_neurons)
        return _decoder

    def _train_system(self, training_code, training_info, training_info_bit,
                      **kwargs):
        _decoder = self.decoder
        _decoder.train(training_code, training_info_bit, **kwargs)
        return _decoder

    def decode_messages(self, messages, channel=None):
        _pred_info = self.decoder.predict(messages)
        _pred_info_bit = np.clip(_pred_info, 0, 1)
        _pred_info_bit = np.round(_pred_info_bit)
        return _pred_info_bit

    def __str__(self):
        return "ElmDecoder"

    def __repr__(self):
        return repr(self.decoder)


class NeuralNetDecoder(MachineLearningDecoder):
    """Decoder class to decode channel codes using feed forward neural networks

    Parameters
    ----------
    layer : list (int)
        Number of nodes in each layer.

    train_snr : float
        Training SNR in dB.

    activation : str
        Activation function used for all hidden layers. See the Keras
        documentation for details.

    loss : str, optional
        Name of loss function. Default: 'binary_crossentropy'.

    kwargs : keyword arguments
        All arguements that are accepted by the Keras `keras.models.compile`
        method.
    """
    def __init__(self, code_length, info_length, layer, train_snr=2.,
                 activation='relu', one_hot=False,
                 optimizer='adam', loss='binary_crossentropy', **kwargs):
        #TODO:Add some logging and storing of history...
        self.one_hot = one_hot
        self.train_snr = train_snr
        super().__init__(code_length, info_length, activation=activation,
                         layer=layer, optimizer=optimizer, loss=loss, **kwargs)

    # Copied from https://github.com/gruberto/D-ChannelDecoding (1701.07738v1)
    @staticmethod
    def __compose_model(layers):
        model = Sequential()
        for layer in layers:
            model.add(layer)
        return model

    def _create_decoder(self, layer, activation, **kwargs):
        if not layer:
            _layers = [layers.InputLayer(input_shape=(self.code_length,))]
        else:
            _layers = [layers.Dense(layer[0], input_shape=(self.code_length,),
                                    activation=activation)]
        _layers.extend([layers.Dense(k, activation=activation)
                        for k in layer[1:]])
        if self.one_hot:
            kwargs['loss'] = 'categorical_crossentropy'
            _layers.append(layers.Dense(2**self.info_length,
                                        activation='softmax'))
        else:
            _layers.append(layers.Dense(self.info_length,
                                        activation='sigmoid'))
        decoder = self.__compose_model(_layers)
        decoder.compile(**kwargs)
        
        #train_snr_lin = 10**(train_snr/10.)
        #TODO:This is only for BPSK with +-1 modulation
        #noise_layer = layers.GaussianNoise(
        #    np.sqrt(1./(2*(self.info_length/self.code_length)*train_snr_lin)),
        #    input_shape=(self.code_length,))
        #train_model = self.__compose_model([noise_layer]+_layers)
        #train_model.compile(**kwargs)
        #return decoder#, train_model
        return decoder, kwargs

    def _train_system(self, training_code, training_info, training_info_bit,
                      train_snr='self', store_history=False, **kwargs):
        """Accept all kwargs from `keras.models.fit`"""
        if train_snr == 'self':
            train_snr = self.train_snr
        decoder, compile_options = self.decoder
        train_snr_lin = 10**(train_snr/10.)
        input_power = np.var(training_code)
        #_train_noise_power = input_power/(2*(self.info_length/self.code_length)*train_snr_lin)
        _train_noise_power = input_power/(2*train_snr_lin)
        noise_layer = layers.GaussianNoise(np.sqrt(_train_noise_power),
                                           input_shape=(self.code_length,))
        train_model = self.__compose_model([noise_layer]+decoder.layers)
        train_model.compile(**compile_options)
        if self.one_hot:
            _train_info = to_categorical(training_info, 2**self.info_length)
        else:
            _train_info = training_info_bit
        history = train_model.fit(training_code, _train_info, verbose=0, **kwargs)
        if store_history:
            _str_layers = "_".join([str(k.units) for k in decoder.layers])
            history_file = "L{}-T{}-OH{}.hist".format(_str_layers, train_snr,
                                                      int(self.one_hot))
            with open(history_file, 'wb') as _history_file:
                pickle.dump(history.history, _history_file)
        return decoder

    def decode_messages(self, messages, channel=None):
        pred = self.decoder.predict(messages)
        if self.one_hot:
            pred_info = np.argmax(pred, axis=1)
            pred_info = unpack_to_bits(pred_info, self.info_length)
        else:
            pred_info = np.round(pred)
        return pred_info
