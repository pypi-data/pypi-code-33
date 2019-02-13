import logging
import time
from datetime import datetime
from itertools import product

import numpy as np
from sklearn.metrics import accuracy_score

from .modulators import IdentityModulator
from .demodulators import IdentityDemodulator
from .messages import generate_data, unpack_to_bits, pack_to_dec, _generate_data_generator


def create_simulation_var_combinations(sim_var_params):
    """Generate a simulation variable dictionary for a CustomSimulation

    Parameters
    ----------
    sim_var_params : dict
        Dict containing the different variable names as keys and their values
        as values in a list.

    Returns
    -------
    sim_var : list
        List of all different simulation parameters.
    """
    sim_var = []
    for _val_tuple in product(*sim_var_params.values()):
        sim_var.append({k: v for k, v in zip(sim_var_params.keys(), _val_tuple)})
    return sim_var


def single_simulation(encoder, decoder, channel, modulator=IdentityModulator,
                      demodulator=IdentityDemodulator, metric=['ber', 'bler'],
                      test_size=1e6, batch_size=50000, test_data_generator=None,
                      seed=None):
    """Run a single simulation with fixed parameters.

    Parameters
    ----------
    encoder : Encoder
        Encoder instance which is used for encoding messages.

    decoder : Decoder
        Decoder instance which is used for decoding messages.

    channel : Channel
        Channel instance which is used for corrupting the transmitted messages.

    modulator : Modulator, optional
        Modulator instance which is used for modulating the codewords before
        transmission. The default is no modulation.

    demodulator : Demodulator, optional
        Demodulator instance which is used for demodulating the channel output
        before decoding. The default is no demodulation.

    metric : list, optional
        List of metrics which are calculated and returned.

    test_size : int, optional
        Number of messages to be tested.

    batch_size : int, optional
        The number of messages which are processed within one batch. Increasing
        this number may cause memory issues.

    test_data_generator : generator, optional
        Provide a generator instance which return the test data. Overwrites the
        test_size and batch_size keyword.

    seed : int, optional
        Seed which is used for the test_data_generator. If None, a random one,
        will be used.

    Returns
    -------
    results : dict
        Dict containing all simulation results. The keys are the metrics and
        the values are the corresponding metric value.
    """
    code_length = encoder.code_length
    info_length = encoder.info_length
    random_length = encoder.random_length
    errors = {k: 0 for k in metric}
    if test_data_generator is None:
        test_size = int(test_size)
        test_data_generator = _generate_data_generator(
            batch_size=batch_size, info_length=info_length+random_length,
            number=test_size, seed=seed)
    for tx_messages in test_data_generator:
        tx_messages_bit = unpack_to_bits(tx_messages, info_length+random_length)
        tx_codewords = encoder.encode_messages(tx_messages_bit)
        tx_modulated = modulator.modulate_symbols(tx_codewords)
        rx_modulated = channel.transmit_data(tx_modulated)
        rx_codewords = demodulator.demodulate_symbols(rx_modulated)
        rx_messages_bit = decoder.decode_messages(rx_codewords, channel)
        tx_messages_bit = tx_messages_bit[:, :info_length]
        tx_messages = pack_to_dec(tx_messages_bit)
        if 'ber' in metric:
            errors['ber'] += np.count_nonzero(tx_messages_bit != rx_messages_bit)/info_length
        if 'bler' in metric:
            rx_messages = pack_to_dec(rx_messages_bit)
            errors['bler'] += np.count_nonzero(np.ravel(tx_messages) != np.ravel(rx_messages))
    results = {k: v/test_size for k, v in errors.items()}
    return results


class ChannelParameterSimulation(object):
    """Generic class for simulations with different channel parameters.
    
    Use this class for common simulations like SNR-BER simulations. The code
    parameters as well as the encoder and decoder are held constant and only
    the channel parameters are kept constant.
    
    Parameters
    ----------
    encoder : Encoder
        Encoder object used for encoding messages.

    decoder : Decoder
        Decoder object used for decoding the demodulator output.

    channel : Channel
        Channel object used to corrupt the transmitted symbols with noise

    modulator : Modulator, optional
        Modulator object used to modulate the codewords before transmitting.
        Default is to use no modulation.

    demodulator : Demodulator, optional
        Demodulator object used to demodulate the channel output before trying
        to decode it. Default is to use no demodulation.

    logger : logging.Logger, optional
        Logger object which is used to log information about the simulation.
    """
    def __init__(self, encoder, decoder, channel, modulator=IdentityModulator,
                 demodulator=IdentityDemodulator, logger=None):
        self.encoder = encoder
        self.modulator = modulator
        self.channel = channel
        self.demodulator = demodulator
        self.decoder = decoder
        self.logger = logger or logging.getLogger('dummy')

    def simulate(self, test_params, test_size=1e6, metric=['bler', 'ber'],
                 batch_size=50000):
        """Run a simulation with provided options.

        Parameters
        ----------
        test_params : list
            List of simulation variables.

        test_size : int, optional
            Number of test messages.

        metric : list (str), optional
            List of metrics that are calculated. Possible choices are "ber" for
            the bit error rate and "bler" for the block error rate.

        batch_size : int, optional
            Size of the test batches.

        Returns
        -------
        results : dict
            Dict including all the results (metrics) for the evaluated
            simulation variables.
        """
        code_length = self.encoder.code_length
        info_length = self.encoder.info_length
        test_size = int(test_size)
        test_data_generator = _generate_data_generator(batch_size=batch_size,
                number=test_size, info_length=info_length)
        results = {c: {k: 0 for k in metric} for c in test_params}
        for tx_messages in test_data_generator:
            tx_messages_bit = unpack_to_bits(tx_messages, info_length)
            tx_codewords = self.encoder.encode_messages(tx_messages_bit)
            tx_modulated = self.modulator.modulate_symbols(tx_codewords)
            for channel_params in test_params:
                self.channel.set_params(channel_params)
                rx_modulated = self.channel.transmit_data(tx_modulated)
                rx_codewords = self.demodulator.demodulate_symbols(rx_modulated)
                rx_messages_bit = self.decoder.decode_messages(rx_codewords, self.channel)
                if 'ber' in metric:
                    results[channel_params]['ber'] += np.count_nonzero(tx_messages_bit != rx_messages_bit)/info_length
                if 'bler' in metric:
                    rx_messages = pack_to_dec(rx_messages_bit)
                    results[channel_params]['bler'] += np.count_nonzero(np.ravel(tx_messages) != np.ravel(rx_messages))
        results = {c: {k: v/test_size for k, v in errors.items()} for c, errors in results.items()}
        self.logger.info(results)
        return results



class CustomSimulation(object):
    """Fully customizable tranmission simulation.
    
    Parameters
    ----------
    encoder : Encoder
        Class object of Encoder like class

    decoder : Decoder
        Class object of Decoder like class

    channel : Channel
        Class object of Channel like class

    modulator : Modulator, optional
        Class object of Modulator like class

    demodulator : Demodulator, optional
        Class object of Demodulator like class

    logger : Logger, optional
        Logger object from logging package
    """
    def __init__(self, encoder, decoder, channel, modulator=IdentityModulator,
                 demodulator=IdentityDemodulator, logger=None):
        self.encoder = encoder
        self.modulator = modulator
        self.channel = channel
        self.demodulator = demodulator
        self.decoder = decoder
        self.logger = self._create_logger() if logger is None else logger
        #self.logger.info(self.__dict__)

    def _create_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        _log_date = datetime.fromtimestamp(time.time())
        log_date = datetime.strftime(_log_date, "%Y-%m-%d-%H-%M-%S")
        # Only log results (INFO) and WARN/ERR in file
        fh = logging.FileHandler('{}.dat'.format(log_date))
        fh.setLevel(logging.INFO)
        # Stream shows everything
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        file_form = logging.Formatter('%(message)s')  #.500s for truncating str
        con_form = logging.Formatter('%(asctime)s - %(levelname)8s - %(message)s')
        fh.setFormatter(file_form)
        ch.setFormatter(con_form)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger#, log_date

    @staticmethod
    def _default_empty_if_none(x):
        return {} if x is None else x

    def simulate(self, simulation_parameters, channel_options,
                 enc_opt=None, dec_opt=None,
                 mod_opt=None, demod_opt=None, training_opt=None, **kwargs):
        self.logger.info(self.__dict__)
        enc_opt = self._default_empty_if_none(enc_opt)
        dec_opt = self._default_empty_if_none(dec_opt)
        mod_opt = self._default_empty_if_none(mod_opt)
        demod_opt = self._default_empty_if_none(demod_opt)
        self.logger.info(enc_opt)
        self.logger.info({k: v for k, v in dec_opt.items() if k != "training_data"})
        self.logger.info(mod_opt)
        self.logger.info(demod_opt)
        self.logger.info(kwargs)

        self.logger.debug("Start simulation...")
        results = {}
        for idx, parameters in enumerate(simulation_parameters):
            #self.logger.info("{}|{}".format(idx, parameters))
            _key = tuple([(k, v) for k, v in parameters.items()])
            self.logger.info(_key)
            results[_key] = {}
            self.logger.debug("Creating encoder...")
            encoder = self.encoder(**{**enc_opt, **parameters})
            modulator = self.modulator(**{**mod_opt, **parameters})
            demodulator = self.demodulator(**{**demod_opt, **parameters})
            self.logger.debug("Creating decoder...")
            decoder = self.decoder(**{**dec_opt, **parameters})
            if training_opt is not None:
                self.logger.debug("Start training...")
                decoder.train_system((encoder, modulator), **training_opt)
                self.logger.debug("...Training finished")
            for _channel_options in channel_options:
                try:
                    _channel_options = tuple(_channel_options)
                except TypeError:
                    _channel_options = (_channel_options,)
                channel = self.channel(*_channel_options)
                results[_key][_channel_options] = single_simulation(
                    encoder=encoder, decoder=decoder, modulator=modulator,
                    demodulator=demodulator, channel=channel, **kwargs)
                self.logger.debug("{}: {}".format(_channel_options, results[_key][_channel_options]))
            self.logger.info(results[_key])
        return results


class HyperparameterSearchDecoderSimulation(object):
    """Class for a hyperparameter grid search for a machine learning decoder.

    The system is assumed to have a constant encoder, modulator and demodulator.
    The hyperparameters of the decoder system will be adjusted and tested for
    different channel parameters.

    Parameters
    ----------
    encoder : encoders.Encoder
        Encoder object which will be used to generate the codewords.

    decoder_class : decoders.MachineLearningDecoder <class>
        Decoder class which will be instantiated with the `decoder_variables`.

    channel_class : channels.Channel <class>
        Channel class which will be instantiated with the `channel_variables`.

    decoder_variables : dict
        Dict containing the hyperparameters of the decoder to be varied. The
        dict will be used to create a grid of all possible combinations.

    channel_variables : dict
        Dict containing the parameters of the channel to be varied for each
        evaluation. The dict will be used to create a grid of all possible
        combinations.

    modulator : modulators.Modulator, optional
        Modulator object which will be used to modulate the codewords.

    demodulator : demodulators.Demodulator, optional
        Demodulator object which will be used to demodulate the codewords.

    logger : logging.Logger, optional
        Logger object which is used for the simulation output. If None, a
        default one will be used.
    """
    def __init__(self, encoder, decoder_class, channel_class, decoder_variables,
                 channel_variables, modulator=IdentityModulator,
                 demodulator=IdentityDemodulator, logger=None):
        self.encoder = encoder
        self.decoder_class = decoder_class
        self.channel_class = channel_class
        self.modulator = modulator
        self.demodulator = demodulator
        self.dec_var = create_simulation_var_combinations(decoder_variables)
        self.channel_var = create_simulation_var_combinations(channel_variables)
        self.logger = self.create_logger() if logger is None else logger

    @staticmethod
    def create_logger(filename=None):
        #logger = logging.getLogger(name="hyperparameter_simulation-{}".format(np.random.randint(0, 1000)))
        logger = logging.getLogger(name=filename)
        logger.setLevel(logging.DEBUG)
        if filename is None:
            filename = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")
        fh = logging.FileHandler('{}.dat'.format(filename))
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        file_form = logging.Formatter('%(message)s')  #.500s for truncating str
        con_form = logging.Formatter('%(asctime)s - [%(levelname)8s]: %(message)s')
        fh.setFormatter(file_form)
        ch.setFormatter(con_form)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger#, log_date

    def start_simulation(self, test_size=1000, metric=['ber', 'bler'],
                         training_options=None, seed=None):
        """Start the full simulation with all possible settings.

        Parameters
        ----------
        test_size : int, optional
            Number of test messages for evaluation.

        metric : list, optional
            List of metrics that should be calculated. Valid choices are `ber`
            and `bler`.

        training_options : dict, optional
            Keyword arguments, which are passed to 
            MachineLearningDecoder.train_system.

        seed : int, optional
            Seed for initializing the test set. This is only used for the data
            generation of the test messages. If None, a random seed will be used.

        Returns
        -------
        simulation_results : list
            List of simulation results. Each element is a tuple of the evaluated
            hyperparameters and the simulation results.
        """
        if seed is None:
            seed = np.random.randint(0, 1000)
        if training_options is None:
            training_options = {}
        self.logger.debug("Starting simulation")
        code_length = self.encoder.code_length
        info_length = self.encoder.info_length
        random_length = self.encoder.random_length
        constants = {'code_length': code_length, 'info_length': info_length,
                     'random_length': random_length, 'test_size': test_size,
                     'seed': seed, 'training_options': training_options}
        constant_elems = {'encoder': repr(self.encoder),
                          'decoder': repr(self.decoder_class),
                          'channel': repr(self.channel_class),
                          'modulator': repr(self.modulator),
                          'demodulator': repr(self.demodulator),
                         }
        self.logger.debug("Constant simulation parameters:")
        self.logger.info({**constants, **constant_elems})
        self.logger.debug("Creating training set...")
        train_info, train_code = self.encoder.generate_codebook()
        train_code = self.modulator.modulate_symbols(train_code)
        simulation_results = []
        for hyperparams in self.dec_var:
            self.logger.debug("Starting evaluation of hyperparameters:")
            self.logger.info(hyperparams)
            _decoder = self.decoder_class(code_length, info_length, **hyperparams)
            self.logger.debug("Starting training of the decoder...")
            _decoder.train_system((train_code, train_info), **training_options)
            results = {}
            for channel_opt in self.channel_var:
                self.logger.debug("Evaluating with channel parameters: %s", channel_opt)
                _channel = self.channel_class(**channel_opt)
                _results = single_simulation(self.encoder, _decoder, _channel,
                        self.modulator, self.demodulator, metric, test_size,
                        seed=seed)
                self.logger.debug("Results: %s", _results)
                _key = tuple([(k, v) for k, v in channel_opt.items()])
                results[_key] = _results
            self.logger.debug("Results for hyperparameter combination:")
            self.logger.info(results)
            simulation_results.append((hyperparams, results))
        return simulation_results
